import tomllib
from pathlib import Path

import click

from clippt.app import PresentationApp
from clippt.slides import Slide, load


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
def clippt(source: Path):
    slides, title = load_slides(source)
    app = PresentationApp(slides=slides, title=title)
    app.run()


def load_slides(source: Path) -> tuple[list[Slide], str]:
    match source.suffix.lower():
        case ".md" | ".markdown" | ".csv" | ".py" | ".pq" | ".parquet":
            return [load(source)], source.stem
        case ".toml":
            with source.open("rb") as f:
                data = tomllib.load(f)
            return [data["slides"]], data["title"]
        case _:
            raise ValueError(f"Unsupported file type: {source.suffix}")


if __name__ == "__main__":
    clippt()
