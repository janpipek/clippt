import io
import json
import tomllib
from pathlib import Path
from typing import Iterable, Literal

from pydantic import BaseModel, Field

from clippt.slides import (
    CodeSlide,
    ErrorSlide,
    MarkdownSlide,
    PythonSlide,
    ShellSlide,
    Slide,
    load,
)


class SlideDescription(BaseModel):
    """Description of a single slide."""

    class Config:
        extra = "forbid"

    type: Literal["python", "shell", "markdown", "code"] | None = None
    source: str | None = None
    path: Path | None = None
    """Path relative to the presentation."""

    title: str | None = None
    language: str | None = None
    """Language to be used for syntax highlighting."""

    alt_screen: bool | None = None
    mode: Literal["code", "output"] | None = None
    runnable: bool | None = None
    wait_for_key: bool | None = None

    classes: list[str] | None = None
    cwd: Path | None = None
    execute_before: str | None = None


class Presentation(BaseModel):
    """Description of a presentation."""

    slide_base_path: Path | None = Field(None, description="Base directory for slides")
    shell_cwd: Path | None = Field(
        None,
        description="Base directory for shell commands, relative to slide_base_path",
    )

    title: str | None = None
    slides: list[SlideDescription | str] = Field(default_factory=list)

    def _get_full_slide_path(self, path: Path) -> Path:
        if path.is_absolute():
            return path
        return (self.slide_base_path or Path(".")) / path

    @property
    def full_shell_cwd(self) -> Path | None:
        return (
            self._get_full_slide_path(self.shell_cwd)
            if self.shell_cwd
            else self.slide_base_path
        )

    def create_slides(self) -> Iterable[Slide]:
        for s in self.slides:
            if isinstance(s, str):
                slide_path = self._get_full_slide_path(Path(s))
                if slide_path.exists():
                    yield load(slide_path, cwd=self.full_shell_cwd)
                else:
                    yield ErrorSlide(source=f"Slide not found: {slide_path}")
            elif isinstance(s, SlideDescription):
                cwd = self._get_full_slide_path(s.cwd) if s.cwd else self.full_shell_cwd
                if s.path:
                    yield load(
                        path=self._get_full_slide_path(s.path),
                        **s.model_dump(
                            exclude_none=True, exclude={"type", "path", "cwd"}
                        ),
                    )
                else:
                    match s.type:
                        case "python":
                            yield PythonSlide(
                                **s.model_dump(exclude_none=True, exclude={"type"})
                            )
                        case "shell":
                            yield ShellSlide(
                                cwd=cwd,
                                **s.model_dump(
                                    exclude_none=True, exclude={"type", "cwd"}
                                ),
                            )
                        case "markdown":
                            yield MarkdownSlide(
                                **s.model_dump(
                                    exclude_none=True,
                                    exclude={"type", "title", "language"},
                                )
                            )
                        case "code":
                            yield CodeSlide(
                                **s.model_dump(exclude_none=True, exclude={"type"})
                            )
                        case None:
                            if s.language:
                                yield CodeSlide(
                                    **s.model_dump(exclude_none=True, exclude={"type"})
                                )
                            else:
                                yield MarkdownSlide(
                                    **s.model_dump(
                                        exclude_none=True,
                                        exclude={"type", "title", "language"},
                                    )
                                )



def load_presentation(path_or_file: Path | str | io.TextIOBase, /) -> Presentation:
    if isinstance(path_or_file, io.TextIOBase):
        content = path_or_file.read()
        pwd = Path(".")
        data = tomllib.loads(content)
        return Presentation.model_validate(data | {"pwd": pwd})
    else:
        path = Path(path_or_file)
        pwd = path.parent

        match path.suffix.lower():
            case ".toml":
                data = tomllib.loads(path.read_text())
                return Presentation.model_validate(data | {"pwd": pwd})
            case ".json":
                data = json.loads(path.read_text())
                return Presentation.model_validate(data | {"pwd": pwd})
            case _:
                raise ValueError(f"Cannot parse {path}")
