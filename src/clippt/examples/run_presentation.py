from io import StringIO

from clippt.model import PresentationModel
from clippt.app import PresentationApp
from clippt.presentation import Presentation

PRESENTATION = {
    "title": "My Presentation",
    "slides": [
        {"source" : "# This is slide 1"},
        {"source" : "import this", "type" : "python" },
    ]
}


if __name__ == "__main__":
    model = PresentationModel.model_validate(PRESENTATION)
    presentation = Presentation.from_model(model)

    presentation

    app = PresentationApp(presentation)
    app.run()
