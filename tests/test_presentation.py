from pathlib import Path
import pytest
from pytest_check import check

from clippt.presentation import load_presentation
from clippt.slides import CodeSlide


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
