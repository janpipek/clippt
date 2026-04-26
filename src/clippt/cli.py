from pathlib import Path
import sys
import shlex

import click

from clippt.app import PresentationApp
from clippt.presentation import Presentation


def common_options(func):
    func = click.option("--no-footer", is_flag=True, help="Disable footer.")(func)
    func = click.option("--no-header", is_flag=True, help="Disable header.")(func)
    func = click.option(
        "--continue", "-c", "continue_", is_flag=True, help="Continue from last slide."
    )(func)
    func = click.option("--serve", "-s", is_flag=True, help="Start a web server")(func)
    func = click.option("-v", "--verbose", count=True)(func)
    return func


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
@common_options
def clippt(*, source: Path, verbose: int, **kwargs):
    """Run a presentation in the command-line."""
    _apply_log_level(verbose)
    presentation = Presentation.from_path(source)
    run_cli(
        presentation=presentation,
        **kwargs,
    )


def run_cli(
    *,
    presentation: Presentation,
    no_footer: bool,
    no_header: bool,
    continue_: bool,
    serve: bool,
):
    app = PresentationApp(presentation=presentation)
    app.enable_footer = not no_footer
    app.enable_header = not no_header
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


def create_cli_command(presentation: Presentation):
    """Create a CLI command for a concrete presentation.

    Useful when using clippt as a library."""

    def app(*, verbose: int, **kwargs):
        _apply_log_level(verbose)
        run_cli(
            presentation=presentation,
            **kwargs,
        )

    app.__doc__ = (
        f"""Present '{presentation.title}'."""
        if presentation.title
        else "Run the presentation"
    )
    app = common_options(app)
    app = click.command()(app)
    return app


def _apply_log_level(verbose: int) -> None:
    log_level = "DEBUG" if verbose > 1 else "INFO" if verbose > 0 else "WARNING"
    import logging

    logging.basicConfig(level=log_level)


if __name__ == "__main__":
    clippt()
