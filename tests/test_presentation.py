import io
from pathlib import Path
import pytest
from pytest_check import check

from clippt.presentation import Presentation
from clippt.slides import CodeSlide, EmptySlide


class TestPresentationFromPath:
    @pytest.mark.parametrize(
        "path",
        [
            pytest.param("fibonacci/presentation.toml", id="separate"),
            pytest.param("fibonacci-inline.toml", id="inline"),
        ],
    )
    def test_load_fibonacci(self, path):
        rel_path = Path(__file__).parent.parent / "src" / "clippt" / "examples" / path
        presentation = Presentation.from_path(rel_path)
        assert len(presentation.slides) == 11
        for slide in presentation.slides[1:]:
            check.is_instance(slide, CodeSlide)

    def test_load_empty_slide(self):
        content = """
            [[ slides ]]
            title = "Empty slide"
        """
        presentation = Presentation.from_path(io.StringIO(content))
        assert len(presentation.slides) == 1
        assert isinstance(presentation.slides[0], EmptySlide)
