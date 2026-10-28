from __future__ import annotations

import json
from dataclasses import dataclass
from typing import NoReturn

from schemamask.errors import CliError

PRINTABLE_START = 32
PRINTABLE_END = 127
PRINTABLE: set[str] = {chr(codepoint) for codepoint in range(PRINTABLE_START, PRINTABLE_END)}

DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
DEFAULT_DIGITS = 3
DEFAULT_STRING_MIN = 0
DEFAULT_STRING_MAX = 8
DEFAULT_ARRAY_MIN = 0
DEFAULT_ARRAY_MAX = 3
MIN_ALPHABET_LENGTH = 1
MAX_ALPHABET_LENGTH = 16
MAX_STRING_LENGTH = 16
MAX_DIGITS = 6
MAX_ARRAY_ITEMS = 5
MIN_ENUM_VALUES = 1
MAX_ENUM_VALUES = 8
MAX_ENUM_STRING_LENGTH = 16
ENUM_INTEGER_LIMIT = 1_000_000
MAX_PROPERTIES = 6
MIN_PROPERTY_NAME_LENGTH = 1
MAX_PROPERTY_NAME_LENGTH = 16
MIN_ALTERNATIVES = 2
MAX_ALTERNATIVES = 4
LOWERCASE_A = ord("a")
LOWERCASE_Z = ord("z")


@dataclass(frozen=True)
class Const:
    """A finite set of complete compact JSON texts."""

    texts: tuple[str, ...]


@dataclass(frozen=True)
class Digits:
    """An integer document with a bounded number of digits."""

    count: int


@dataclass(frozen=True)
class Chars:
    """A string document with a restricted character alphabet and length."""

    alphabet: str
    low: int
    high: int


@dataclass(frozen=True)
class Seq:
    """An array of recursively described items."""

    item: Node
    low: int
    high: int


@dataclass(frozen=True)
class Record:
    """An object with required, ordered properties."""

    names: tuple[str, ...]
    nodes: tuple[Node, ...]


@dataclass(frozen=True)
class Choice:
    """A choice among recursively described alternatives."""

    options: tuple[Node, ...]


Node = Const | Digits | Chars | Seq | Record | Choice


def is_int(value: object) -> bool:
    """Return whether value is an integer other than a boolean."""
    return isinstance(value, int) and not isinstance(value, bool)


def parse_schema(value: object, label: str) -> Node:
    """Parse a schema value and report the first problem with its location."""
    return _parse(value, label, "$")


def _fail(label: str, path: str, detail: str) -> NoReturn:
    message = f"schemamask: {label}: {path}: {detail}"
    raise CliError(message)


def _parse(value: object, label: str, path: str) -> Node:
    if not isinstance(value, dict):
        _fail(label, path, "must be an object")
    return _parse_object(value, label, path)


def _parse_object(schema: dict[object, object], label: str, path: str) -> Node:
    if "anyOf" in schema:
        _check_keys(schema, ("anyOf",), label, path)
        return _parse_choice(schema["anyOf"], label, path)
    if "enum" in schema:
        _check_keys(schema, ("enum",), label, path)
        return _parse_enum(schema["enum"], label, path)

    type_value = schema.get("type")
    if not isinstance(type_value, str):
        _check_keys(schema, ("type",), label, path)
        if "type" not in schema:
            _fail(label, path, 'missing "type"')
        _fail(label, path, '"type" must be a string')

    allowed = _type_keys(type_value)
    _check_keys(schema, allowed, label, path)
    if type_value not in _TYPE_NAMES:
        _fail(label, path, f'unknown type "{type_value}"')
    return _parse_kind(type_value, schema, label, path)


def _type_keys(type_name: str) -> tuple[str, ...]:
    if type_name == "integer":
        return ("type", "maxDigits")
    if type_name == "string":
        return ("type", "alphabet", "minLength", "maxLength")
    if type_name == "array":
        return ("type", "items", "minItems", "maxItems")
    if type_name == "object":
        return ("type", "properties")
    return ("type",)


_TYPE_NAMES = {"boolean", "null", "integer", "string", "array", "object"}


def _check_keys(
    schema: dict[object, object], allowed: tuple[str, ...], label: str, path: str
) -> None:
    for key in schema:
        if key not in allowed:
            _fail(label, path, f'unknown keyword "{key}"')


def _parse_kind(type_name: str, schema: dict[object, object], label: str, path: str) -> Node:
    if type_name == "boolean":
        return Const(("true", "false"))
    if type_name == "null":
        return Const(("null",))
    if type_name == "integer":
        return _parse_digits(schema, label, path)
    if type_name == "string":
        return _parse_chars(schema, label, path)
    if type_name == "array":
        return _parse_sequence(schema, label, path)
    if type_name == "object":
        return _parse_record(schema, label, path)
    _fail(label, path, f'unknown type "{type_name}"')


def _bounded_int(value: object, field: str, low: int, high: int, location: tuple[str, str]) -> int:
    if not is_int(value) or value < low or value > high:
        label, path = location
        _fail(label, path, f'"{field}" must be an integer from {low} to {high}')
    return value


def _parse_digits(schema: dict[object, object], label: str, path: str) -> Digits:
    value = schema.get("maxDigits", DEFAULT_DIGITS)
    count = _bounded_int(value, "maxDigits", 1, MAX_DIGITS, (label, path))
    return Digits(count)


def _valid_alphabet(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if not MIN_ALPHABET_LENGTH <= len(value) <= MAX_ALPHABET_LENGTH:
        return False
    if len(set(value)) != len(value):
        return False
    return all(character in PRINTABLE and character not in {'"', "\\"} for character in value)


def _parse_chars(schema: dict[object, object], label: str, path: str) -> Chars:
    if "alphabet" in schema:
        alphabet_value = schema["alphabet"]
        if not _valid_alphabet(alphabet_value):
            _fail(
                label,
                path,
                '"alphabet" must be 1 to 16 distinct printable ASCII characters '
                "without quote or backslash",
            )
        alphabet = alphabet_value
    else:
        alphabet = DEFAULT_ALPHABET

    low = _bounded_int(
        schema.get("minLength", DEFAULT_STRING_MIN),
        "minLength",
        0,
        MAX_STRING_LENGTH,
        (label, path),
    )
    high = _bounded_int(
        schema.get("maxLength", DEFAULT_STRING_MAX),
        "maxLength",
        0,
        MAX_STRING_LENGTH,
        (label, path),
    )
    if low > high:
        _fail(label, path, '"minLength" is larger than "maxLength"')
    return Chars(alphabet, low, high)


def _valid_enum_string(value: str) -> bool:
    return len(value) <= MAX_ENUM_STRING_LENGTH and all(
        character in PRINTABLE and character not in {'"', "\\"} for character in value
    )


def _valid_enum_value(value: object) -> bool:
    if isinstance(value, str):
        return _valid_enum_string(value)
    if is_int(value):
        return -ENUM_INTEGER_LIMIT < value < ENUM_INTEGER_LIMIT
    return isinstance(value, bool) or value is None


def _parse_enum(value: object, label: str, path: str) -> Const:
    if not isinstance(value, list) or not MIN_ENUM_VALUES <= len(value) <= MAX_ENUM_VALUES:
        _fail(label, path, '"enum" must be an array of 1 to 8 values')

    texts: list[str] = []
    seen: set[str] = set()
    for index, entry in enumerate(value, start=1):
        if not _valid_enum_value(entry):
            _fail(
                label,
                path,
                f'"enum" value {index} is not a short string, integer, boolean or null',
            )
        text = json.dumps(entry, separators=(",", ":"))
        if text in seen:
            _fail(label, path, '"enum" has a duplicate value')
        texts.append(text)
        seen.add(text)
    return Const(tuple(texts))


def _parse_sequence(schema: dict[object, object], label: str, path: str) -> Seq:
    if "items" not in schema:
        _fail(label, path, 'missing "items"')
    item = _parse(schema["items"], label, f"{path}.items")
    low = _bounded_int(
        schema.get("minItems", DEFAULT_ARRAY_MIN),
        "minItems",
        0,
        MAX_ARRAY_ITEMS,
        (label, path),
    )
    high = _bounded_int(
        schema.get("maxItems", DEFAULT_ARRAY_MAX),
        "maxItems",
        0,
        MAX_ARRAY_ITEMS,
        (label, path),
    )
    if low > high:
        _fail(label, path, '"minItems" is larger than "maxItems"')
    return Seq(item, low, high)


def _valid_property_name(name: object) -> bool:
    if not isinstance(name, str):
        return False
    if not MIN_PROPERTY_NAME_LENGTH <= len(name) <= MAX_PROPERTY_NAME_LENGTH:
        return False
    return all(
        character == "_" or LOWERCASE_A <= ord(character) <= LOWERCASE_Z for character in name
    )


def _parse_record(schema: dict[object, object], label: str, path: str) -> Record:
    if "properties" not in schema:
        _fail(label, path, 'missing "properties"')
    properties = schema["properties"]
    if not isinstance(properties, dict):
        _fail(label, path, '"properties" must be an object')
    if len(properties) > MAX_PROPERTIES:
        _fail(label, path, '"properties" has more than 6 entries')

    names: list[str] = []
    nodes: list[Node] = []
    for name, child in properties.items():
        if not _valid_property_name(name):
            _fail(
                label,
                path,
                f'property name "{name}" is not 1 to 16 lowercase letters or underscores',
            )
        property_name = name
        names.append(property_name)
        nodes.append(_parse(child, label, f"{path}.properties.{property_name}"))
    return Record(tuple(names), tuple(nodes))


def _parse_choice(value: object, label: str, path: str) -> Choice:
    if not isinstance(value, list) or not MIN_ALTERNATIVES <= len(value) <= MAX_ALTERNATIVES:
        _fail(label, path, '"anyOf" must be an array of 2 to 4 schemas')

    options: list[Node] = []
    for index, option in enumerate(value):
        options.append(_parse(option, label, f"{path}.anyOf[{index}]"))
    return Choice(tuple(options))
