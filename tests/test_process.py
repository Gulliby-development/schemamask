import subprocess
import sys


def test_bad_utf8_on_stdin_exits_two() -> None:
    done = subprocess.run(
        [sys.executable, "-m", "schemamask", "check", "-"],
        input=b"\xff",
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert done.returncode == 2
    assert done.stdout == b""
    assert done.stderr == b"schemamask: <stdin>: input is not valid UTF-8\n"
