import os
import sys

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
