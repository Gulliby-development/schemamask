"""Top-level command dispatch and result routing."""

from collections.abc import Callable
from dataclasses import dataclass

from schemamask.cmd_allowed import run_allowed
from schemamask.cmd_check import run_check
from schemamask.cmd_decode import run_decode
from schemamask.cmd_validate import run_validate
from schemamask.envio import Env
from schemamask.errors import CliError

USAGE = (
    "usage: schemamask COMMAND [ARGS]\n"
    "  check SCHEMA\n"
    "  allowed SCHEMA VOCAB [--prefix TEXT]\n"
    "  decode SCHEMA VOCAB SCRIPT [--max-steps N] [--no-mask] [--brief]\n"
    "  validate SCHEMA TEXT\n"
)


@dataclass(frozen=True)
class Result:
    """A command's exit status and captured output streams."""

    exit: int
    out: str
    err: str


def run(
    args: list[str],
    stdin: bytes,
    read: Callable[[str], bytes | None],
) -> Result:
    """Dispatch a command and convert expected CLI errors into results."""
    if not args:
        return Result(2, "", USAGE.rstrip("\n") + "\n")

    command = args[0]
    if command in {"help", "-h", "--help"}:
        return Result(0, USAGE, "")

    if command not in {"check", "allowed", "decode", "validate"}:
        message = f'schemamask: unknown command "{command}"'
        return Result(2, "", message + "\n")

    env = Env(stdin, read)
    try:
        if command == "check":
            exit_code, output = run_check(args[1:], env)
        elif command == "allowed":
            exit_code, output = run_allowed(args[1:], env)
        elif command == "decode":
            exit_code, output = run_decode(args[1:], env)
        elif command == "validate":
            exit_code, output = run_validate(args[1:], env)
    except CliError as error:
        return Result(error.code, "", error.message + "\n")

    return Result(exit_code, output, "")
