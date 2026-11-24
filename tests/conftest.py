from pathlib import Path

from clippt import Presentation
import pytest


@pytest.fixture
def empty_presentation() -> Presentation:
    return Presentation(
        slides=[], title="Simple presentation", slide_base_path=Path(".")
    )
