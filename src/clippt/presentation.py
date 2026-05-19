from pathlib import Path

from pydantic import BaseModel, Field

from clippt.model import PresentationModel, SlideModel
from clippt.slides import (
    Slide,
    load_slide,
)


class Presentation(BaseModel):
    """Presentation, holding a bunch of slides."""

    slides: list[Slide] = Field(default_factory=list)
    title: str | None = None
    slide_base_path: Path

    @staticmethod
    def _create_slide(slide: SlideModel | str, *, slide_base_path: Path) -> Slide:
        if isinstance(slide, str):
            path = slide_base_path / slide
            return load_slide(path)
        else:
            return Slide.from_model(slide, base_path=slide_base_path)

    @classmethod
    def from_model(
        cls, model: PresentationModel, *, slide_base_path: Path = Path(".")
    ) -> "Presentation":
        """Create the presentation from a pydantic description."""
        return Presentation(
            title=model.title,
            slides=[
                cls._create_slide(slide, slide_base_path=slide_base_path)
                for slide in model.slides
            ],
            slide_base_path=slide_base_path,
        )

    @classmethod
    def from_path(cls, path_or_file: Path | str) -> "Presentation":
        """Load the presentation from the external file."""
        model = PresentationModel.from_path(path_or_file)
        slide_base_path = Path(path_or_file).absolute()
        if not slide_base_path.is_dir():
            slide_base_path = slide_base_path.parent
        presentation = cls.from_model(model, slide_base_path=slide_base_path)
        return presentation

    @property
    def slides_count(self) -> int:
        """Total number of slides."""
        return len(self.slides)

    def add_slide(self, slide: Slide) -> None:
        self.slides.append(slide)
