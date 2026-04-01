def demo():
    from clippt import load_presentation, PresentationApp
    import importlib.resources

    presentation_toml = importlib.resources.files("clippt") / "examples" / "clippt" / "presentation.toml"
    with importlib.resources.as_file(presentation_toml) as path:
        presentation = load_presentation(path)
        slides = presentation.create_slides()
        app = PresentationApp(
            slides=slides, title=presentation.title or "", shell_cwd=presentation.shell_cwd
        )
        app.run()