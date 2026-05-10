"""Theming and styling for clippt.

Useful links:
- https://textual.textualize.io/widgets/markdown/#textual.widgets._markdown.Markdown.BLOCKS
"""

css_tweaks: str = """
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
    Markdown {
      MarkdownH1 {
        margin: 1 0;
      }
    }
    MarkdownFence {
        margin: 1;
        max-height: 500;
    }
    Static.output {
        margin: 0 0;
        max-height: 500;
        padding: 1 1;
    }
    Static.error {
        background: #ffcccc;
        color: #800000;
        margin: 0 3;
        max-height: 500;
        padding: 1 2;
    }
"""
"""Additional CSS styling for the presentation app."""
