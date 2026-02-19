from pathlib import Path

import click

import os

from clippt.app import PresentationApp
from clippt.slides import Slide, load
from clippt.presentation import load_presentation


@click.command()
@click.argument(
    "source",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        path_type=Path,
    ),
)
@click.option("--disable-footer", is_flag=True, help="Disable footer.")
@click.option(
    "--continue", "-c", "continue_", is_flag=True, help="Continue from last slide."
)
@click.option("--dev", is_flag=True, help="Enable textual dev tools.")
def clippt(*, source: Path, disable_footer: bool, continue_: bool, dev: bool):
    """Run a presentation in the command-line."""

    slides, title = load_slides(source)
    app = PresentationApp(slides=slides, title=title)
    app.enable_footer = not disable_footer
    if dev:
        os.environ["TEXTUAL"] = "debug,devtools"
    if continue_ and Path(".current_slide").exists():
        app.slide_index = int(Path(".current_slide").read_text())
    app.slide_index = min(app.slide_index, len(slides) - 1)
    app.run()


def load_slides(source: Path) -> tuple[list[Slide], str]:
    if source.is_dir():
        if (source / "presentation.toml").exists():
            source = source / "presentation.toml"
        else:
            raise FileNotFoundError(f"presentation.toml not found in {source}")

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
