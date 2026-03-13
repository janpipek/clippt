from pathlib import Path
import sys
import shlex

import click

from clippt.app import PresentationApp
from clippt.presentation import load_presentation, Presentation


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
@click.option(
    "--serve", "-s", is_flag=True, help="Start a web server"
)
def clippt(*, source: Path, disable_footer: bool, continue_: bool, serve: bool):
    """Run a presentation in the command-line."""
    presentation = create_presentation(source)
    slides = list(presentation.create_slides())
    app = PresentationApp(
        slides=slides, title=presentation.title or "", shell_cwd=presentation.shell_cwd
    )
    app.enable_footer = not disable_footer
    if continue_ and Path(".current_slide").exists():
        app.current_slide_index = int(Path(".current_slide").read_text())
    app.current_slide_index = min(app.current_slide_index, len(slides) - 1)

    if serve:
        from textual_serve.server import Server

        command_args = sys.argv
        # Remove serve flag from args (could be either --serve or -s)
        for flag in ["--serve", "-s"]:
            try:
                command_args.remove(flag)
                break
            except ValueError:
                pass
        serve_command = shlex.join(command_args)
        server = Server(
            serve_command,
            host="localhost",
            port=23456,
            title=serve_command,
            public_url=None,
        )
        server.serve()
    else:
        app.run()


def create_presentation(source: Path) -> Presentation:
    if source.is_dir():
        if (source / "presentation.toml").exists():
            source = source / "presentation.toml"
        else:
            raise FileNotFoundError(f"presentation.toml not found in {source}")

    match source.suffix.lower():
        case ".md" | ".markdown" | ".csv" | ".py" | ".pq" | ".parquet":
            return Presentation(slides=[str(source)])
        case ".toml":
            presentation = load_presentation(source)
            return presentation
        case _:
            raise ValueError(f"Unsupported file type: {source.suffix}")


if __name__ == "__main__":
    clippt()
