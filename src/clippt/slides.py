import io
import subprocess
import traceback
from abc import ABC, abstractmethod
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable, Literal, Optional, Final

import polars as pl
from pydantic import BaseModel, model_validator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from shellingham import detect_shell
from textual.app import App
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Markdown, Static
from textual_fastdatatable import DataTable
from textual_fastdatatable.backend import PolarsBackend

from clippt.utils import wait_for_key


class Slide(ABC, BaseModel):
    path: Path | None = None
    source: str = ""
    runnable: bool = False

    @model_validator(mode="after")
    def _load_on_start(self):
        self._load()
        return self

    def _load(self):
        if self.path:
            try:
                self.source = self.path.read_text(encoding="utf-8")
            except FileNotFoundError:
                self.source = f"File not found: {self.path}."

    def reload(self):
        self._load()

    @abstractmethod
    def render(self, app: App) -> Widget: ...

    def run(self) -> None:
        pass


class CodeSlide(Slide):
    language: str | None = None
    title: Optional[str] = None
    is_title_markdown: bool = False

    def render(self, app) -> Widget:
        return self._render_code()

    def _render_code(self) -> VerticalScroll:
        code_lines = []
        for line in self.source.splitlines():
            line = line.rstrip()
            if "# HIDE_ABOVE" in line:
                code_lines = []
                continue
            if "# HIDE_BELOW" in line:
                break
            if "# HIDE" in line:
                continue
            code_lines.append(line)
        code = "\n".join(line for line in code_lines)
        if self.title:
            if self.is_title_markdown:
                md = Markdown(self.title + f"\n\n```{self.language}\n{code}\n```")
            else:
                md = Markdown(f"# {self.title}\n\n```{self.language}\n{code}\n```")
        else:
            md = Markdown(f"```{self.language}\n{code}\n```")
        return VerticalScroll(md, can_focus=False)


class ExecutableSlide(CodeSlide, ABC):
    """Slide with runnable code from external file or string."""

    mode: Literal["code", "output"] = "code"
    alt_screen: bool = False
    runnable: bool = True
    wait_for_key: bool = False
    is_error: bool = False

    _output: str | None = None

    def _load(self):
        self._output = None
        super()._load()

    def render(self, app) -> Widget:
        match self.mode:
            case "code":
                return self._render_code()
            case "output":
                if self.alt_screen:
                    self._exec_in_alternate_screen(app)
                    return self._render_code()
                else:
                    output = self._exec_inline(app)
                    return self._render_output(output=output, app=app)

    def _render_output(self, *, output: str, app: App) -> Widget:
        classes = "error" if self.is_error else "output"
        output_widget = Static(Text.from_ansi(output + "\n"), classes=classes)
        if self.title:
            if self.is_title_markdown:
                return VerticalScroll(
                    Markdown(self.title), output_widget, can_focus=False
                )
            return VerticalScroll(
                Markdown(f"# {self.title}"), output_widget, can_focus=False
            )
        return VerticalScroll(output_widget, can_focus=False)

    @abstractmethod
    def _exec_inline(self, app: App) -> str:
        """Execute the code and return the output."""

    @abstractmethod
    def _exec(self, app: App):
        """Execute the code."""

    def run(self):
        self.mode = "output" if self.mode == "code" else "code"

    def _exec_in_alternate_screen(self, app):
        with app.suspend():
            console = Console()
            console.clear()
            self._exec(app)
            if self.wait_for_key:
                wait_for_key()
            self.mode = "code"
            console.clear()


class PythonSlide(ExecutableSlide):
    language: Final[str] = "python"

    def _exec_inline(self, app) -> str:
        f = io.StringIO()
        with redirect_stdout(f):
            # TODO: Rethink? Remnant of old project, 99% not needed.
            # import plotext as plt
            # plt.plotsize(width=50, height=15)

            try:
                self._exec(app=app)
                return f.getvalue()
            except Exception as ex:
                out = StringIO()
                out.write(f"Error: {ex}\n")
                out.write("\n")
                traceback.print_exception(ex, file=out)
                return out.getvalue()

    def _exec(self, app: App) -> None:
        self.is_error = False
        try:
            exec(
                self.source,
                globals=globals()
                | {
                    "WIDTH": app.size.width - (10 if self.title else 4),
                    "HEIGHT": app.size.height - 2,
                },
            )
        except Exception:
            self.is_error = True
            raise

        # TODO: Rethink? Remnant of old project, 99% not needed.
        # import plotext as plt
        # plt.clear_figure()


class ShellSlide(ExecutableSlide):
    language: Final[str] = "shell"
    _executed: bool = False

    def __post_init__(self, **kwargs):
        if not self.source.strip():
            _, self.source = detect_shell()

    def _load(self):
        self._executed = False
        super()._load()

    def _exec(self, app: App):
        return subprocess.run(
            self.source.strip(),
            shell=True,
            capture_output=not self.alt_screen,
            text=True,
            encoding="utf-8",
        )

    def _exec_inline(self, app) -> str:
        if not self._executed:
            with app.suspend():
                p = self._exec(app)
                self._output = p.stdout or p.stderr
                # TODO: Maybe we should raise if it fails and handle it elsewhere
                self.is_error = (p.returncode != 0)
                self._executed = True
        return self._output


class MarkdownSlide(Slide):
    classes: Optional[str] = None

    """Markdown slide with source from external file or string."""

    def render(self, app: App) -> Markdown:
        return Markdown(dedent(self.source), classes=self.classes)


class TextSlide(Slide):
    title: Optional[str] = None

    def render(self, app: App) -> VerticalScroll:
        widgets = []
        if self.title:
            widgets.append(Markdown(f"# {self.title}"))
        widgets.append(Static(self.source))
        return VerticalScroll(*widgets, can_focus=False)


class FuncSlide(Slide):
    """Any slide created from a function."""

    f: Callable[[App], Markdown | Text | str]
    source: str = ""  # ignored
    path: None = None  # ignored

    def render(self, app: App) -> Widget:
        rendered = self.f(app)
        if isinstance(rendered, Widget):
            return rendered
        elif isinstance(rendered, str):
            return Markdown(dedent(rendered))
        elif isinstance(rendered, (Text, Panel)):
            return Static(rendered)
        else:
            raise NotImplementedError()


class DataSlide(Slide):
    data: Optional[pl.DataFrame] = None

    class Config:
        arbitrary_types_allowed = True

    def render(self, app: App) -> Widget:
        if self.data is not None:
            backend = PolarsBackend.from_dataframe(self.data)
            dt = DataTable(backend=backend, zebra_stripes=True, show_cursor=False)
            dt.can_focus = False
            return dt
        else:
            return Markdown("No data.")

    def _load(self) -> None:
        if self.path:
            match self.path.suffix:
                case ".csv":
                    self.data = pl.read_csv(self.path)
                case ".pq" | ".parquet":
                    self.data = pl.read_parquet(self.path)
                case _:
                    raise NotImplementedError()


def slide(f: Callable[[App], Any]) -> FuncSlide:
    """Decorator to create a markdown slide from a function."""
    return FuncSlide(f=f)


def md(source: str, **kwargs) -> MarkdownSlide:
    """Helper function to create a simple Markdown slide."""
    return MarkdownSlide(path=None, source=source, **kwargs)


def py(source: str, **kwargs) -> ExecutableSlide:
    """Helper function to create a simple Python code slide."""
    return PythonSlide(path=None, source=source, **kwargs)


def sh(cmd, **kwargs) -> ExecutableSlide:
    """Helper function to create a shell command slide."""
    return ShellSlide(source=cmd, **kwargs)


def load(path: str | Path, **kwargs) -> Slide:
    """Load a slide from an external file."""
    path = Path(path)
    match path.suffix:
        case ".py":
            return PythonSlide(path=path, **kwargs)
        case ".md":
            return MarkdownSlide(path=path, **kwargs)
        case ".csv" | ".pq" | ".parquet":
            return DataSlide(path=path, **kwargs)
        case ".txt":
            return TextSlide(path=path, **kwargs)
        case other:
            language = kwargs.pop("language", EXT_LANGUAGE_MAPPING.get(other, "text"))
            return CodeSlide(path=path, language=language, **kwargs)


EXT_LANGUAGE_MAPPING = {
    ".json": "json",
    ".toml": "toml",
    ".yaml": "yaml",
    ".rs": "rust",
    ".scm": "scheme",
    ".go": "go",
}
