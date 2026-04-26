import os
import subprocess
from pathlib import Path

import click
import shellingham
from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import QueryError
from textual.widgets import Footer, Header

from clippt.slides import Slide, ErrorSlide
from clippt.theming import css_tweaks
from clippt.presentation import Presentation


class PresentationApp(App):
    """Textual app for the presentation."""

    enable_footer: bool = True
    enable_header: bool = True

    BINDINGS = [
        ("pageup", "prev_slide", "Previous"),
        ("pagedown", "next_slide", "Next"),
        (".", "run", "Run"),
        ("q", "quit", "Quit"),
        ("e", "edit", "Edit"),
        ("r", "reload", "Reload"),
        ("home", "first_slide", "First slide"),
        ("end", "last_slide", "Last slide"),
        ("ctrl+o", "shell", "Shell"),
    ]

    CSS = css_tweaks

    current_slide_index: reactive[int] = reactive(0, init=False)
    """Index of the slide displayed (updates the view when set)."""

    presentation: Presentation

    shell_cwd: Path | None = None

    def __init__(
        self,
        presentation: Presentation,
        *,
        shell_cwd: Path | None = None,
        **kwargs,
    ):
        if not presentation.slides:
            self.presentation = Presentation(
                slides=[
                    ErrorSlide(source="**Error**: Empty presentation"),
                ]
            )
        else:
            self.presentation = presentation

        self.shell_cwd = shell_cwd
        super().__init__(**kwargs)
        self.title = presentation.title

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        if self.enable_header:
            yield Header()
        yield Container(
            self.current_slide.render(app=self),
            id="content",  # , can_focus=False
        )
        if self.enable_footer:
            yield Footer(show_command_palette=False)

    def watch_current_slide_index(self, old_value: int, new_value: int) -> None:
        self._update_slide()

    def on_mount(self) -> None:
        """Hook called when the app is mounted."""
        # self.register_theme(my_theme)
        self.theme = "textual-light"

    def on_resize(self) -> None:
        """Hook called when the app is resized."""
        self._update_slide()

    def action_reload(self) -> None:
        self.current_slide.reload()
        self._update_slide()

    def action_next_slide(self) -> None:
        self.current_slide_index = min(
            self.current_slide_index + 1, self.presentation.slides_count - 1
        )

    def action_prev_slide(self) -> None:
        self.current_slide_index = max(self.current_slide_index - 1, 0)

    def action_first_slide(self) -> None:
        self.current_slide_index = 0

    def action_last_slide(self) -> None:
        self.current_slide_index = self.presentation.slides_count - 1

    def action_edit(self) -> None:
        if self.current_slide.path:
            with self.suspend():
                click.edit(
                    filename=[str(self.current_slide.path)],
                    editor=os.environ.get("EDITOR"),
                )
            self.current_slide.reload()
        self._update_slide()

    def action_run(self) -> None:
        if self.current_slide.runnable:
            self.current_slide.run()
            self._update_slide()
            # No need to refresh() - update_slide() handles the refresh

    @property
    def current_slide(self) -> Slide:
        return self.presentation.slides[self.current_slide_index]

    def action_shell(self):
        """Run a shell in the alternate screen."""
        with self.suspend():
            _, shell = shellingham.detect_shell()
            subprocess.run(shell, shell=True, capture_output=False, cwd=self.shell_cwd)

    def _update_slide(self) -> None:
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
            content_widget = self.current_slide.render(app=self)
            container_widget.mount(content_widget)
            self.sub_title = (
                f"{self.current_slide_index + 1} / {self.presentation.slides_count}"
            )

            Path(".current_slide").write_text(str(self.current_slide_index))
        except QueryError:
            pass
