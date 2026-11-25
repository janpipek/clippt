def demo():
    import importlib.resources

    from clippt import Presentation, PresentationApp

    presentation_toml = importlib.resources.files("clippt") / "examples" / "clippt" / "presentation.toml"
    with importlib.resources.as_file(presentation_toml) as path:
        presentation = Presentation.from_path(path)
        app = PresentationApp(
           presentation=presentation
        )
        app.run()