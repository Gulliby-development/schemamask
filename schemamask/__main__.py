"""Entry point: python -m schemamask."""

import sys
from pathlib import Path

from schemamask.cli import run


def read_file(path: str) -> bytes | None:
    try:
        return Path(path).read_bytes()
    except OSError:
        return None


def main() -> int:
    args = sys.argv[1:]
    stdin = sys.stdin.buffer.read() if "-" in args else b""
    result = run(args, stdin, read_file)
    sys.stdout.buffer.write(result.out.encode("utf-8"))
    sys.stderr.buffer.write(result.err.encode("utf-8"))
    return result.exit


if __name__ == "__main__":
    raise SystemExit(main())
