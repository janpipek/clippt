import tomllib
from itertools import chain
from pathlib import Path
from typing import Any

import click
from typing_extensions import Iterable

from clippt.app import PresentationApp
from clippt.slides import MarkdownSlide, PythonSlide, ShellSlide, Slide, load


@click.command()
@click.argument(
    "source",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
    ),
)
@click.option("--disable-footer", is_flag=True, help="Disable footer.")
def clippt(source: Path, disable_footer: bool):
    slides, title = load_slides(source)
    app = PresentationApp(slides=slides, title=title)
    app.enable_footer = not disable_footer
    app.run()


def load_slides(source: Path) -> tuple[list[Slide], str]:
    def _load_single(item: Any) -> Iterable[Slide]:
        if isinstance(item, str):
            yield load(source.parent / item)
        if isinstance(item, dict):
            content = item.get("content", "")
            title = item.get("title", None)
            alt_screen = item.get("alt_screen", False)
            mode = item.get("mode", "code")
            match item.get("type", "markdown"):
                case "markdown":
                    if title:
                        content = f"# {title}\n\n{content}"
                    yield MarkdownSlide(content)
                case "python":
                    yield PythonSlide(
                        source=content, title=title, alt_screen=alt_screen, mode=mode
                    )
                case "shell":
                    yield ShellSlide(
                        source=content, title=title, alt_screen=alt_screen, mode=mode
                    )
                case _:
                    raise ValueError(f"Unsupported slide type: {item['type']}")

    match source.suffix.lower():
        case ".md" | ".markdown" | ".csv" | ".py" | ".pq" | ".parquet":
            return [load(source)], source.stem
        case ".toml":
            with source.open("rb") as f:
                data = tomllib.load(f)
            slides = list(
                chain(*(_load_single(item) for item in data.get("slides", [])))
            )
            return slides, data.get("title", source.stem)
        case _:
            raise ValueError(f"Unsupported file type: {source.suffix}")


if __name__ == "__main__":
    clippt()
