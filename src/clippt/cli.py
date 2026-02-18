import tomllib
from itertools import chain
from pathlib import Path
from typing import Any

import click
from typing_extensions import Iterable

from clippt.app import PresentationApp
from clippt.slides import MarkdownSlide, PythonSlide, ShellSlide, Slide, load
from clippt.presentation import load_presentation


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
@click.option(
    "--continue", "-c", "continue_", is_flag=True, help="Continue from last slide."
)
def clippt(source: Path, disable_footer: bool, continue_: bool):
    slides, title = load_slides(source)
    app = PresentationApp(slides=slides, title=title)
    app.enable_footer = not disable_footer
    if continue_ and Path(".current_slide").exists():
        app.slide_index = int(Path(".current_slide").read_text())
    app.slide_index = min(app.slide_index, len(slides) - 1)
    app.run()


def load_slides(source: Path) -> tuple[list[Slide], str]:
    def _load_single(item: Any) -> Iterable[Slide]:
        if isinstance(item, str):
            yield load(source.parent / item)
        if isinstance(item, dict):
            content = item.get("content", "")
            path = (
                source.parent / Path(path_str)
                if (path_str := item.get("path"))
                else None
            )
            if not content and path:
                content = path.read_text(encoding="utf-8")
            title = item.get("title", None)
            alt_screen = item.get("alt_screen", False)
            mode = item.get("mode", "code")
            match item.get("type", "markdown"):
                case "markdown":
                    if title:
                        content = f"# {title}\n\n{content}"
                    yield MarkdownSlide(content, path=path)
                case "python":
                    yield PythonSlide(
                        source=content,
                        title=title,
                        alt_screen=alt_screen,
                        mode=mode,
                        path=path,
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
            presentation = load_presentation(source)
            slides = list(presentation.create_slides())
            return slides, presentation.title or source.stem
        case _:
            raise ValueError(f"Unsupported file type: {source.suffix}")


if __name__ == "__main__":
    clippt()
