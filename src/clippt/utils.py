import os
import sys
from contextlib import contextmanager

import rich


def wait_for_key():
    """Wait for a key press from the user."""
    rich.print("[bold]Press any key to continue...[/bold]")
    match sys.platform:
        case "win32":
            import msvcrt

            msvcrt.getch()
        case "linux" | "darwin":
            # Test this works on mac
            import termios
            import tty

            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            try:
                os.read(sys.stdin.fileno(), 3).decode()
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


@contextmanager
def patch_environment(kwargs: dict[str, str]):
    """Temporarily change the environment variables."""
    old_environ: dict[str, str | None] = {k: os.environ.get(k) for k in kwargs}
    os.environ.update(kwargs)
    try:
        yield
    finally:
        for k, v in kwargs.items():
            del os.environ[k]
            if (v := old_environ[k]) is not None:
                os.environ[k] = v
