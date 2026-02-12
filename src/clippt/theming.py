from textual.theme import Theme

my_theme = Theme(
    name="my",
    primary="#0000c0",
    secondary="#4040ff",
    accent="#00ff00",
    foreground="#444444",
    background="#ffffff",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#ffffff",
    panel="#ffffff",
    dark=False,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)

css_tweaks = """
    Screen {
        align: center middle;
    }
    Footer {
        background: #ffffd0;
        color: white;
        dock: bottom;
        height: 1;
    }
    Markdown.title {
        MarkdownFence {
            background: white;
            margin: 0;
        }
    }
    MarkdownFence {
        background: #fff9e4; /* Light yellow */
        margin: 1;
        max-height: 500;
    }
 """
