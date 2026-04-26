from pathlib import Path
import sys
import shlex

import click

from clippt.app import PresentationApp
from clippt.presentation import Presentation


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
@click.option("--serve", "-s", is_flag=True, help="Start a web server")
@click.option("-v", "--verbose", count=True)
def clippt(
    *, source: Path, disable_footer: bool, continue_: bool, serve: bool, verbose: int
):
    """Run a presentation in the command-line."""

    log_level = "DEBUG" if verbose > 1 else "INFO" if verbose > 0 else "WARNING"
    import logging

    logging.basicConfig(level=log_level)

    presentation = Presentation.from_path(source)
    app = PresentationApp(presentation=presentation)
    app.enable_footer = not disable_footer
    if continue_ and Path(".current_slide").exists():
        app.slide_index = int(Path(".current_slide").read_text())
    app.slide_index = min(app.slide_index, len(presentation.slides) - 1)

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


if __name__ == "__main__":
    clippt()
