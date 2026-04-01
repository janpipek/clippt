import io
from pathlib import Path
import pytest
from pytest_check import check

from clippt.presentation import load_presentation
from clippt.slides import CodeSlide, EmptySlide


class TestLoadPresentation:
    @pytest.mark.parametrize(
        "path",
        [
            pytest.param("fibonacci/presentation.toml", id="separate"),
            pytest.param("fibonacci-inline.toml", id="inline"),
        ],
    )
    def test_load_fibonacci(self, path):
        rel_path = Path(__file__).parent.parent / "examples" / path
        presentation = load_presentation(rel_path)
        slides = list(presentation.create_slides())
        assert len(slides) == 11
        for slide in slides[1:]:
            check.is_instance(slide, CodeSlide)

    def test_load_empty_slide(self):
        content = """
            [[ slides ]]
            title = "Empty slide"
        """
        presentation = load_presentation(io.StringIO(content))
        slides = list(presentation.create_slides())
        assert len(slides) == 1
        assert isinstance(slides[0], EmptySlide)
