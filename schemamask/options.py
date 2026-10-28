"""Shared parsing and validation for command-line options."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import NoReturn

from schemamask.errors import CliError

MIN_BOUNDED_VALUE = 1
MIN_BOUNDED_DIGITS = 1
MAX_BOUNDED_DIGITS = 3
MAX_STDIN_ARGUMENTS = 1


@dataclass
class Parsed:
    """Parsed positional arguments and option values."""

    positionals: list[str]
    values: dict[str, str]


def _unknown_option(option: str) -> NoReturn:
    message = f'schemamask: unknown option "{option}"'
    raise CliError(message)


def _option_needs_value(option: str) -> NoReturn:
    message = f"schemamask: option {option} needs a value"
    raise CliError(message)


def _option_takes_no_value(option: str) -> NoReturn:
    message = f"schemamask: option {option} takes no value"
    raise CliError(message)


def split(args: list[str], takes_value: Mapping[str, bool]) -> Parsed:
    """Split configured options from positionals while preserving their order."""
    positionals: list[str] = []
    values: dict[str, str] = {}
    index = 0

    while index < len(args):
        argument = args[index]
        if argument == "-" or not argument.startswith("-"):
            positionals.append(argument)
            index += 1
            continue

        option, separator, inline_value = argument.partition("=")
        if option not in takes_value:
            _unknown_option(option)
        if separator:
            if not takes_value[option]:
                _option_takes_no_value(option)
            values[option] = inline_value
        elif takes_value[option]:
            if index + 1 >= len(args):
                _option_needs_value(option)
            index += 1
            values[option] = args[index]
        else:
            values[option] = ""
        index += 1

    return Parsed(positionals, values)


def need(parsed: Parsed, low: int, high: int, command: str) -> None:
    """Validate positional argument count and reject repeated stdin markers."""
    count = len(parsed.positionals)
    if count < low or count > high:
        message = f"schemamask: {command}: wrong number of arguments"
        raise CliError(message)
    if parsed.positionals.count("-") > MAX_STDIN_ARGUMENTS:
        message = "schemamask: standard input can be read once"
        raise CliError(message)


def _is_bounded_decimal(text: str) -> bool:
    return (
        MIN_BOUNDED_DIGITS <= len(text) <= MAX_BOUNDED_DIGITS and text.isascii() and text.isdigit()
    )


def _bad_bounded_value(text: str, name: str, high: int) -> NoReturn:
    message = (
        f'schemamask: bad {name} value "{text}": '
        f"expected an integer from {MIN_BOUNDED_VALUE} to {high}"
    )
    raise CliError(message)


def bounded(text: str, name: str, high: int) -> int:
    """Parse an ASCII decimal value in the inclusive range from one to high."""
    if not _is_bounded_decimal(text):
        _bad_bounded_value(text, name, high)
    value = int(text)
    if value < MIN_BOUNDED_VALUE or value > high:
        _bad_bounded_value(text, name, high)
    return value
