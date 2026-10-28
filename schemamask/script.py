"""Immutable model script loading and validation."""

from dataclasses import dataclass
from typing import NoReturn

from schemamask.errors import CliError
from schemamask.textio import load_json

MAX_IDS_PER_STEP = 16
STRUCTURE_ERROR = '"steps" must be an array of arrays of up to 16 token ids'
RANGE_ERROR = '"steps" holds an id outside the vocabulary'
FALLBACK_ERROR = '"fallback" must be "lowest" or "highest"'


@dataclass(frozen=True)
class Script:
    """An ordered sequence of token-id preferences and its fallback policy."""

    steps: tuple[tuple[int, ...], ...]
    fallback: str


def _fail(label: str, detail: str) -> NoReturn:
    message = f"schemamask: {label}: {detail}"
    raise CliError(message)


def _read_steps(value: object, label: str) -> list[list[int]]:
    if not isinstance(value, list):
        _fail(label, STRUCTURE_ERROR)

    result: list[list[int]] = []
    for step in value:
        if not isinstance(step, list) or len(step) > MAX_IDS_PER_STEP:
            _fail(label, STRUCTURE_ERROR)

        parsed_step: list[int] = []
        for token_id in step:
            if not isinstance(token_id, int) or isinstance(token_id, bool):
                _fail(label, STRUCTURE_ERROR)
            parsed_step.append(token_id)
        result.append(parsed_step)
    return result


def _check_ranges(steps: list[list[int]], size: int, label: str) -> None:
    for step in steps:
        for token_id in step:
            if token_id < 0 or token_id >= size:
                _fail(label, RANGE_ERROR)


def load_script(data: bytes, label: str, size: int) -> Script:
    """Load and validate a script against the vocabulary size."""
    value = load_json(data, label)
    if not isinstance(value, dict):
        _fail(label, "must be an object")

    for key in value:
        if key not in ("steps", "fallback"):
            _fail(label, f'unknown keyword "{key}"')

    steps = _read_steps(value.get("steps", []), label)
    _check_ranges(steps, size, label)

    fallback = value.get("fallback", "lowest")
    if fallback not in ("lowest", "highest"):
        _fail(label, FALLBACK_ERROR)

    return Script(tuple(tuple(step) for step in steps), fallback)
