from pathlib import Path
from textwrap import dedent

from clippt.app import PresentationApp
from clippt.slides import ErrorSlide, MarkdownSlide
from clippt.presentation import Presentation

import pytest


@pytest.fixture
def markdown_slide() -> MarkdownSlide:
    source = """# Example

    Hello world.
    """
    return MarkdownSlide(source=dedent(source))


@pytest.mark.asyncio
class TestApp:
    async def test_run_simple_presentation(self, markdown_slide):
        presentation = Presentation(
            slides=[markdown_slide],
            title="Simple presentation",
            slide_base_path=Path("."),
        )
        app = PresentationApp(presentation)
        async with app.run_test():
            assert app.current_slide == markdown_slide

    async def test_run_empty_presentation(self, empty_presentation):
        app = PresentationApp(empty_presentation)
        async with app.run_test():
            assert isinstance(app.current_slide, ErrorSlide)
