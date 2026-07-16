import os
import subprocess
from collections.abc import Iterable
from pathlib import Path

import click
import shellingham
from textual.reactive import reactive
from textual.app import App, ComposeResult, SystemCommand, ScreenStackError
from textual.containers import Container
from textual.css.query import QueryError
from textual.screen import Screen
from textual.widgets import Footer, Header

from clippt.slides import Slide, ErrorSlide
from clippt.theming import css_tweaks
from clippt.presentation import Presentation


class PresentationApp(App):
    """Textual app for the presentation."""

    presentation: Presentation

    slide_index: reactive[int] = reactive(0, init=False)
    """Index of the current slide displayed (updates the view when set)."""

    enable_footer: reactive[bool] = reactive(True)
    enable_header: reactive[bool] = reactive(True)

    BINDINGS = [
        ("pageup", "prev_slide", "Previous"),
        ("pagedown", "next_slide", "Next"),
        (".", "run", "Run"),
        ("q", "quit", "Quit"),
        ("e", "edit", "Edit"),
        ("r", "reload", "Reload"),
        ("home", "first_slide", "First"),
        ("end", "last_slide", "Last"),
        ("ctrl+o", "shell", "Shell"),
        ("h", "toggle_header", "Toggle header"),
        ("f", "toggle_footer", "Toggle footer"),
    ]

    CSS = css_tweaks

    working_dir: Path = Path(".")
    """Directory in which commands and scripts are executed."""

    def __init__(
        self,
        presentation: Presentation,
        **kwargs,
    ):
        if not presentation.slides:
            self.presentation = presentation.model_copy(
                update={"slides": [ErrorSlide(source="No slide in the presentation.")]}
            )
        else:
            self.presentation = presentation

        super().__init__(**kwargs)
        self.working_dir = self.presentation.slide_base_path
        self.title = presentation.title
        self.theme = kwargs.pop("theme", "textual-light")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            id="content",  # , can_focus=False
        )
        yield Footer(show_command_palette=True)

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        # Commands defined by textual
        yield from super().get_system_commands(screen)

        # Commands available as bound actions
        for action in self.BINDINGS:
            attr_name = f"action_{action[1]}"
            if attr_name in self.__class__.__dict__:
                attr = getattr(self, attr_name)
                if callable(attr):
                    doc = attr.__doc__.splitlines()[0].rstrip(".")
                    yield SystemCommand(action[2], doc, attr)

    def watch_slide_index(self, old_value: int, new_value: int) -> None:
        """Hook called when the current slide index changes"""
        self._update_slide()

    def on_resize(self) -> None:
        """Hook called when the app is resized."""
        # TODO: Update only slides that need it.
        self._update_slide()

    @property
    def current_slide(self) -> Slide:
        return self.presentation.slides[self.slide_index]

    def action_shell(self):
        """Run a shell in the alternate screen"""
        with self.suspend():
            _, shell = shellingham.detect_shell()
            subprocess.run(
                shell, shell=True, capture_output=False, cwd=self.working_dir
            )

    def action_reload(self) -> None:
        """Reload current slide"""
        self.current_slide.reload()
        self._update_slide()

    def action_next_slide(self) -> None:
        """Go to the next slide"""
        self.slide_index = min(self.slide_index + 1, self.presentation.slides_count - 1)

    def action_prev_slide(self) -> None:
        """Go to the previous slide"""
        self.slide_index = max(self.slide_index - 1, 0)

    def action_first_slide(self) -> None:
        """Go to the first slide."""
        self.slide_index = 0

    def action_last_slide(self) -> None:
        """Got to the last slide"""
        self.slide_index = self.presentation.slides_count - 1

    def action_edit(self) -> None:
        """Edit the current slide's source code"""
        if self.current_slide.path:
            with self.suspend():
                click.edit(
                    filename=[str(self.current_slide.path)],
                    editor=os.environ.get("EDITOR"),
                )
            self.current_slide.reload()
        self._update_slide()

    def action_run(self) -> None:
        """Toggle between the source code and output.

        This causes any executable slide to run.
        """
        if self.current_slide.runnable:
            self.current_slide.toggle_output()
            self._update_slide()
            # No need to refresh() - update_slide() handles the refresh

    def _update_slide(self) -> None:
        """Render the current slide and update the view."""
        try:
            container_widget = self.query_one("#content", Container)
            if not container_widget.is_attached:
                return
            container_widget.remove_children()
            # No need to refresh() - mounting will trigger automatic refresh
            self.log(
                "Rendering slide",
                {"type": self.current_slide.__class__.__name__}
                | self.current_slide.model_dump(),
            )
            columns = self.size.width - 2  # For scrollbar
            rows = (
                self.size.height - bool(self.enable_footer) - bool(self.enable_header)
            )
            content_widget = self.current_slide.render(
                app=self, columns=columns, rows=rows
            )
            container_widget.mount(content_widget)
            self.sub_title = (
                f"{self.slide_index + 1} / {self.presentation.slides_count}"
            )

            Path(".current_slide").write_text(str(self.slide_index))
        except (QueryError, ScreenStackError):
            pass

    def action_toggle_footer(self) -> None:
        """Show / hide the application footer"""
        self.enable_footer = not self.enable_footer
        self.query_one(Footer).display = self.enable_footer

    def action_toggle_header(self) -> None:
        """Show / hide the application header"""
        self.enable_header = not self.enable_header
        self.query_one(Header).display = self.enable_header
