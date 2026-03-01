from textwrap import dedent
from clippt.app import PresentationApp
from clippt.slides import ErrorSlide, MarkdownSlide


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
        app = PresentationApp(slides=[markdown_slide], title="Simple app")
        async with app.run_test():
            assert app.current_slide == markdown_slide

    async def test_run_empty_presentation(self):
        app = PresentationApp(slides=[], title="")
        async with app.run_test():
            assert isinstance(app.current_slide, ErrorSlide)
