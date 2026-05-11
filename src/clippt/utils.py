import os
import sys
from contextlib import contextmanager
import subprocess
from pathlib import Path

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


def exec_in_pseudo_terminal(
    *, command: str, cwd: Path | None, columns: int, rows: int
) -> tuple[str, bool]:
    match sys.platform:
        case "win32":
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=cwd,
                env=get_terminal_env_vars(columns, rows),
            )
            return proc.stdout or proc.stderr, proc.returncode != 0

        case "linux" | "darwin":
            # Assisted by Claude (a bit of magic)
            import termios
            import struct
            import fcntl
            import pty

            master_fd, slave_fd = pty.openpty()

            # Set the window size on the slave end so TIOCSWINSZ returns our value
            winsize = struct.pack("HHHH", rows, columns, 0, 0)
            fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

            attrs = termios.tcgetattr(slave_fd)
            attrs[1] &= ~termios.ONLCR  # clear the nl→crnl output flag
            termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)

            with patch_environment(get_terminal_env_vars(columns, rows)):
                proc = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    close_fds=True,
                    cwd=cwd,
                )
            os.close(slave_fd)

            chunks = []
            while True:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break  # Linux: EIO when slave is fully closed
                if not data:
                    break  # macOS/BSD: EOF (0 bytes) when slave is fully closed
                chunks.append(data)

            proc.wait()
            os.close(master_fd)
            return b"".join(chunks).decode(), proc.returncode != 0

        case _:
            raise NotImplementedError("Not implemented for this platform.")


def get_terminal_env_vars(columns: int, rows: int) -> dict[str, str]:
    return {
        "COLUMNS": str(columns),
        "LINES": str(rows),
        "FORCE_COLOR": "1",
    }


@contextmanager
def patch_environment(kwargs: dict[str, str]):
    """Temporarily change the environment variables."""
    old_environ: dict[str, str | None] = {k: os.environ.get(k) for k in kwargs}
    os.environ.update(kwargs)
    try:
        yield
    finally:
        for key, v in kwargs.items():
            try:
                del os.environ[key]
            except KeyError:
                pass  # TODO: This should not happen but does occasionally
            if (old_value := old_environ[key]) is not None:
                os.environ[key] = old_value
