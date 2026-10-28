import json

from schemamask.errors import CliError


def decode_text(data: bytes, label: str) -> str:
    """Decode strict UTF-8, removing only one leading byte-order mark."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        message = f"schemamask: {label}: input is not valid UTF-8"
        raise CliError(message) from error

    if text.startswith("\ufeff"):
        return text[1:]
    return text


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build an object while rejecting duplicate decoded keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            message = "duplicate JSON object key"
            raise ValueError(message)
        result[key] = value
    return result


def _reject_constant(value: str) -> object:
    """Reject the non-standard non-finite constants accepted by json.loads."""
    message = f"non-finite JSON constant: {value}"
    raise ValueError(message)


def load_json(data: bytes, label: str) -> object:
    """Decode a JSON value, enforcing duplicate-key and constant restrictions."""
    text = decode_text(data, label)
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (ValueError, RecursionError) as error:
        message = f"schemamask: {label}: not valid JSON"
        raise CliError(message) from error
