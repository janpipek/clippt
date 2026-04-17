from pathlib import Path

from pydantic import BaseModel, Field

from clippt.model import PresentationModel, SlideModel
from clippt.slides import (
    Slide,
    load_slide,
)


class Presentation(BaseModel):
    slides: list[Slide] = Field(default_factory=list)
    title: str | None = None

    @classmethod
    def from_model(cls, model: PresentationModel) -> "Presentation":
        def _create_slide(s: SlideModel | str):
            if isinstance(s, str):
                path = (model.slide_base_path or Path(".")) / Path(s)
                return load_slide(path, cwd=model.full_shell_cwd)
            else:
                return Slide.from_model(
                    s, base_path=model.slide_base_path, cwd=model.full_shell_cwd
                )

        return Presentation(
            title=model.title, slides=[_create_slide(s) for s in model.slides]
        )

    @classmethod
    def from_path(cls, path: Path) -> "Presentation":
        model = PresentationModel.from_path(path)
        return cls.from_model(model)

    def add_slide(self, slide: Slide) -> None:
        self.slides.append(slide)
