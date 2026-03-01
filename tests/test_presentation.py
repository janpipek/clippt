from pathlib import Path
import pytest

from clippt.presentation import load_presentation

class TestLoadPresentation:
    @pytest.mark.parametrize("path", [
        pytest.param("fibonacci/presentation.toml", id="separate"),
        pytest.param("fibonacci-inline.toml", id="inline")
    ])
    def test_load_fibonacci(self, path):
        rel_path = Path(__file__).parent.parent / "examples" / path
        presentation = load_presentation(rel_path)
        assert len(presentation.slides) == 11
