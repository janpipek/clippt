from io import StringIO

from clippt.app import PresentationApp
from clippt.presentation import load_presentation

CONTENT = """
title = "My Presentation"
slides = [
    {source = "# This is slide 1"},
    {source = "import this", type = "python" },
]
"""
ß
if __name__ == "__main__":
    presentation = load_presentation(StringIO(CONTENT))
    slides = list(presentation.create_slides())
    app = PresentationApp(slides=slides, title=presentation.title or "")
    app.run()
