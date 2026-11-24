"""Static description of the presentation as pydantic models."""

from pydantic import BaseModel, Field
from pathlib import Path
from typing import Literal
import io
import tomllib
import json


class SlideModel(BaseModel):
    """Description of a single slide."""

    model_config = {"extra": "forbid"}

    type: Literal["python", "shell", "markdown", "code"] | None = None
    source: str | None = None
    path: Path | None = None
    """Path relative to the presentation."""

    title: str | None = None
    language: str | None = None
    """Language to be used for syntax highlighting."""

    alt_screen: bool | None = None
    display_mode: Literal["code", "output"] | None = None
    runnable: bool | None = None
    wait_for_key: bool | None = None

    classes: list[str] | None = None


class PresentationModel(BaseModel):
    """Description of a presentation."""

    title: str | None = None
    slides: list[SlideModel | str] = Field(default_factory=list)

    @classmethod
    def from_path(
        cls, path_or_file: Path | str | io.TextIOBase, /
    ) -> "PresentationModel":
        if isinstance(path_or_file, io.TextIOBase):
            content = path_or_file.read()
            data = tomllib.loads(content)
            return PresentationModel.model_validate(data)
        else:
            path = Path(path_or_file)

            if path.is_dir() and (path / "presentation.toml").exists():
                path = path / "presentation.toml"

            match path.suffix.lower():
                case ".toml":
                    data = tomllib.loads(path.read_text())
                    return PresentationModel.model_validate(data)
                case ".json":
                    data = json.loads(path.read_text())
                    return PresentationModel.model_validate(data)
                case _:
                    raise ValueError(f"Cannot parse {path}")
