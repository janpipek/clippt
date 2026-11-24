from textual.widgets import Digits

from clippt.cli import create_cli_command
from clippt.model import PresentationModel
from clippt.presentation import Presentation
from clippt.slides import FuncSlide

PRESENTATION = {
    "title": "My Presentation",
    "slides": [
        {"source" : "# This is slide 1"},
        {"source" : "import this", "type" : "python" },
    ]
}


def clock_widget(app) -> Digits:
    return Digits("42")


if __name__ == "__main__":
    model = PresentationModel.model_validate(PRESENTATION)
    presentation = Presentation.from_model(model)

    # Add a slide that has dynamic content containing widgets
    presentation.add_slide(FuncSlide(f=clock_widget))

    create_cli_command(presentation)()