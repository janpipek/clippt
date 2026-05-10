import contextlib
import io
import subprocess
import traceback
from abc import ABC, abstractmethod
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import Callable, Final, Literal, Optional, Any
import os
import pty
import fcntl
import struct
import termios

import polars as pl
from pydantic import BaseModel, model_validator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from shellingham import detect_shell
from textual.app import App
from textual.containers import VerticalScroll, Vertical
from textual.widget import Widget
from textual.widgets import Markdown, Static
from textual_fastdatatable import DataTable
from textual_fastdatatable.backend import PolarsBackend

from clippt.utils import wait_for_key, patch_environment
from clippt.model import SlideModel


class Slide(ABC, BaseModel):
    """Abstract slide."""

    path: Path | None = None
    source: str = ""
    runnable: bool = False

    execute_before: str | None = None
    """Shell script to execute before the slide is rendered."""

    cwd: Path | None = None

    title: Optional[str] = None
    is_title_markdown: bool = False

    scrollbar: Literal["own", "system", "none"] = "system"
    """Which scrollbars to show."""

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
                self.runnable = False

    def reload(self):
        self._load()

    def render(self, app: App, *, columns: int, rows: int) -> Widget:
        """Create the widgets representing the slide.

        Args:
            app: The textual app rendering the slide (TODO: Change to Presentation app?
            columns: The available number of columns (excluding any margins, scrollbars, etc.)
            rows: The available number of physical rows (including the min. three lines for the title)

        Note that
        """
        if self.execute_before:
            subprocess.run(
                self.execute_before.strip(),
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=self.cwd,
            )
        widgets = []
        if self.title:
            # TODO: We should not support this
            if self.is_title_markdown:
                widgets.append(
                    Markdown(
                        self.title,
                        classes="slide-title",
                    )
                )
                rows -= 3  # This is not correct
            else:
                widgets.append(Markdown(f"# {self.title}", classes="slide-title"))
                rows -= 3
        widgets.append(self._render_impl(app, rows=rows, columns=columns))
        if self.scrollbar in ["own", "none"]:
            if len(widgets) == 1:
                return widgets[0]
            else:
                return Vertical(*widgets)
        return VerticalScroll(*widgets, can_focus=False)

    @abstractmethod
    def _render_impl(self, app: App, *, columns: int, rows: int) -> Widget: ...

    def run(self) -> None:
        pass

    @staticmethod
    def from_model(
        s: SlideModel, *, base_path: Path | None = None, cwd: Path | None = None
    ) -> "Slide":
        if not base_path:
            base_path = Path(".")
        if not cwd:
            cwd = base_path
        if s.path:
            # TODO: Check it is properly relative
            full_path = base_path / s.path
            return load_slide(
                path=full_path,
                cwd=cwd,
                **s.model_dump(exclude_none=True, exclude={"type", "path", "cwd"}),
            )
        else:
            match s.type:
                case "python":
                    return PythonSlide(
                        cwd=cwd, **s.model_dump(exclude_none=True, exclude={"type"})
                    )
                case "shell":
                    return ShellSlide(
                        cwd=cwd,
                        **s.model_dump(exclude_none=True, exclude={"type", "cwd"}),
                    )
                case "markdown":
                    return MarkdownSlide(
                        cwd=cwd,
                        **s.model_dump(
                            exclude_none=True,
                            exclude={"type", "title", "language", "cwd"},
                        ),
                    )
                case "code":
                    return CodeSlide(
                        cwd=cwd,
                        **s.model_dump(exclude_none=True, exclude={"type", "cwd"}),
                    )
                case None:
                    if not s.source:
                        return EmptySlide(
                            cwd=cwd, **s.model_dump(exclude_none=True, exclude={"cwd"})
                        )
                    elif s.language:
                        return CodeSlide(
                            cwd=cwd, **s.model_dump(exclude_none=True, exclude={"cwd"})
                        )
                    else:
                        return MarkdownSlide(
                            cwd=cwd,
                            **s.model_dump(
                                exclude_none=True,
                                exclude={"title", "language", "cwd"},
                            ),
                        )


class EmptySlide(Slide):
    """Slide with no content."""

    def _render_impl(self, app: App) -> Widget:
        return Markdown("")


class CodeSlide(Slide):
    """Slide containing (any) code.

    It is not executable - see :class:`ExecutableSlide` and its subclasses.
    """

    language: str | None = None

    def _render_impl(self, app, *, columns: int, rows: int) -> Widget:
        return self._render_code()

    def _render_code(self) -> Markdown:
        # We do not need columns/rows, the Markdown widget properly formats itself
        if self.path:
            self.reload()
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
        return Markdown(f"```{self.language}\n{code}\n```")


class ExecutableSlide(CodeSlide, ABC):
    """Slide with runnable code from external file or string.

    An abstract base class which has implementation for several
    languages.
    """

    display_mode: Literal["code", "output"] = "code"
    """What is displayed - code or output."""

    alt_screen: bool = False
    """If true, run the code in an alternate, interactive screen."""

    runnable: bool = True

    wait_for_key: bool = False
    """If true, wait for a key press before continuing."""

    is_error: bool = False

    _output: str | None = None

    def _load(self):
        self._output = None
        super()._load()

    def _render_impl(self, app: App, *, columns: int, rows: int) -> Widget:
        match self.display_mode:
            case "code":
                return self._render_code()
            case "output":
                if self.alt_screen:
                    self._exec_in_alternate_screen(app)
                    return self._render_code()
                else:
                    columns -= (
                        3  # Margin of the output (+1 for occasional rendering bugs)
                    )
                    output = self._exec_inline(app, columns=columns, rows=rows)
                    return self._render_output(output=output, app=app)

    @staticmethod
    def _get_terminal_env_vars(columns: int, rows: int) -> dict:
        return {
            "COLUMNS": str(columns),
            "LINES": str(rows),
            "FORCE_COLOR": "1",
        }

    def _render_output(self, *, output: str, app: App) -> Widget:
        classes = "error" if self.is_error else "output"
        return Static(Text.from_ansi(output + "\n"), classes=classes)

    def run(self):
        self.display_mode = "output" if self.display_mode == "code" else "code"

    @contextlib.contextmanager
    def _alternate_screen(self, app: App):
        with app.suspend():
            console = Console()
            console.clear()
            yield
            if self.wait_for_key:
                wait_for_key()
            self.display_mode = "code"
            console.clear()

    @abstractmethod
    def _exec_in_alternate_screen(self, app):
        """Execute the code in an alternate screen."""

    @abstractmethod
    def _exec_inline(self, app: App, *, columns: int, rows: int) -> str:
        """Execute the code and return the output."""


class PythonSlide(ExecutableSlide):
    """Slide with runnable Python code.

    It executes the code directly in the running Python process.
    """

    language: Final[str] = "python"

    def _exec_inline(self, app, *, columns: int, rows: int) -> str:
        f = io.StringIO()
        with patch_environment(self._get_terminal_env_vars(columns, rows)):
            with redirect_stdout(f):
                self.is_error = False
                try:
                    exec(
                        self.source,
                        globals=globals()
                        | {
                            "WIDTH": columns,
                            "HEIGHT": rows,
                        },
                    )
                    return f.getvalue()
                except Exception as ex:
                    self.is_error = True
                    out = StringIO()
                    out.write(f"Error: {ex}\n")
                    out.write("\n")
                    traceback.print_exception(ex, file=out)
                    return out.getvalue()

    def _exec_in_alternate_screen(self, app):
        with self._alternate_screen(app=app):
            exec(
                self.source,
                globals=globals(),
            )


class ShellSlide(ExecutableSlide):
    """Slide with shell command(s)."""

    language: Final[str] = "shell"

    def __post_init__(self, **kwargs):
        if not self.source.strip():
            _, self.source = detect_shell()

    def _exec_in_alternate_screen(self, app: App):
        with self._alternate_screen(app=app):
            env = None
            return subprocess.run(
                self.source.strip(),
                shell=True,
                capture_output=False,
                text=True,
                encoding="utf-8",
                cwd=self.cwd,
                env=env,
            )

    def _exec_inline(self, app, *, columns: int, rows: int) -> str:
        if self._output is None:
            self._output, self.is_error = self._exec_in_pseudo_terminal(columns, rows)
        return self._output

    def _exec_in_pseudo_terminal(self, columns: int, rows: int) -> tuple[str, bool]:
        # Assisted by Claude (a bit of magic)
        master_fd, slave_fd = pty.openpty()

        # Set the window size on the slave end so TIOCGWINSZ returns our value
        winsize = struct.pack("HHHH", rows, columns, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

        attrs = termios.tcgetattr(slave_fd)
        attrs[1] &= ~termios.ONLCR  # clear the nl→crnl output flag
        termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)

        with patch_environment(self._get_terminal_env_vars(columns, rows)):
            proc = subprocess.Popen(
                self.source.strip(),
                shell=True,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
                cwd=self.cwd,
            )
        os.close(slave_fd)

        chunks = []
        while True:
            try:
                chunks.append(os.read(master_fd, 4096))
            except OSError:
                break

        proc.wait()
        os.close(master_fd)
        return b"".join(chunks).decode(), proc.returncode != 0


class MarkdownSlide(Slide):
    """Markdown slide."""

    classes: list[str] | None = None

    def _render_impl(self, app, *, columns: int, rows: int) -> Markdown:
        return Markdown(self.source, classes="slide " + " ".join(self.classes or []))


class TextSlide(Slide):
    title: Optional[str] = None

    def _render_impl(self, app, *, columns: int, rows: int) -> Static:
        return Static(self.source)


class FuncSlide(Slide):
    """Any slide created from a function."""

    f: Callable[[App], Any]
    source: str = ""  # ignored
    path: None = None  # ignored

    def _render_impl(self, app, *, columns: int, rows: int) -> Widget:
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
    """Slide containing data displayed as a table."""

    data: Optional[pl.DataFrame] = None

    model_config = {"arbitrary_types_allowed": True}
    scrollbar: Literal["own"] = "own"

    def _render_impl(self, app, *, columns: int, rows: int) -> Widget:
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


class ErrorSlide(Slide):
    """Slide to display an error message."""

    def _render_impl(self, app, *, columns: int, rows: int) -> Widget:
        return Static(Text.from_ansi(self.source), classes="error")


def load_slide(path: str | Path, **kwargs) -> Slide:
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
