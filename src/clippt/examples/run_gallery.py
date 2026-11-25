from pathlib import Path
from clippt.cli import create_cli_command
from clippt.presentation import Presentation

from clippt.slides import ImageSlide


IMAGES_DIR = Path(__file__).parent / "gallery"

if __name__ == "__main__":
    presentation = Presentation(slide_base_path=Path(__file__).parent.absolute())
    for image_path in IMAGES_DIR.glob("*.jpg"):
        presentation.add_slide(ImageSlide(path=image_path))

    create_cli_command(presentation)()