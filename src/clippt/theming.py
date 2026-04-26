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
        dock: bottom;
        height: 1;
    }
    DataTable {
        height: 1fr;
    }
    Header {
        height: 1;
    }
    Markdown.title {
        MarkdownFence {
            margin: 0;
        }
    }
    Static.slide-title {
        height: 1;
        margin: 1;
        padding: 0;
        content-align: center middle;
        color: $markdown-h1-color;
        background: $markdown-h1-background;
        text-style: $markdown-h1-text-style;        
    } 
    Markdown MarkdownH1 {
        height: 1;
        margin: 1 0;
        padding: 0;
        content-align: center middle;
    }    
    MarkdownFence {
        margin: 1;
        max-height: 500;
    }
    Static.output {
        margin: 0 3;
        max-height: 500;
        padding: 1 2;
    }
    Static.error {
        background: #ffcccc;
        color: #800000;
        margin: 0 3;
        max-height: 500;
        padding: 1 2;
    }
 """
