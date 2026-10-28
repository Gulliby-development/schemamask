import pytest

from schemamask.errors import CliError
from schemamask.schema import Chars, Const, Digits, Seq, parse_schema


def test_parses_every_kind() -> None:
    assert parse_schema({"type": "boolean"}, "s.json") == Const(("true", "false"))
    assert parse_schema({"type": "null"}, "s.json") == Const(("null",))
    assert parse_schema({"type": "integer"}, "s.json") == Digits(3)
    assert parse_schema({"type": "integer", "maxDigits": 2}, "s.json") == Digits(2)
    assert parse_schema({"type": "string"}, "s.json") == Chars("abcdefghijklmnopqrstuvwxyz", 0, 8)
    assert parse_schema(
        {"type": "string", "alphabet": "ab", "minLength": 1, "maxLength": 2}, "s.json"
    ) == Chars("ab", 1, 2)
    assert parse_schema({"enum": [1, "a", True, None, -3]}, "s.json") == Const(
        ("1", '"a"', "true", "null", "-3")
    )
    assert parse_schema({"type": "array", "items": {"type": "null"}}, "s.json") == Seq(
        Const(("null",)), 0, 3
    )


def test_names_the_path_of_a_bad_schema() -> None:
    with pytest.raises(CliError) as caught:
        parse_schema([], "s.json")
    assert caught.value.message == "schemamask: s.json: $: must be an object"
    with pytest.raises(CliError) as caught:
        parse_schema({}, "s.json")
    assert caught.value.message == 'schemamask: s.json: $: missing "type"'
    with pytest.raises(CliError) as caught:
        parse_schema({"type": 3}, "s.json")
    assert caught.value.message == 'schemamask: s.json: $: "type" must be a string'
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "foo"}, "s.json")
    assert caught.value.message == 'schemamask: s.json: $: unknown type "foo"'
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "null", "x": 1}, "s.json")
    assert caught.value.message == 'schemamask: s.json: $: unknown keyword "x"'
    with pytest.raises(CliError) as caught:
        parse_schema({"enum": [], "type": "null"}, "s.json")
    assert caught.value.message == 'schemamask: s.json: $: unknown keyword "type"'
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "integer", "maxDigits": 0}, "s.json")
    assert caught.value.message == (
        'schemamask: s.json: $: "maxDigits" must be an integer from 1 to 6'
    )
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "integer", "maxDigits": 7}, "s.json")
    assert caught.value.message == (
        'schemamask: s.json: $: "maxDigits" must be an integer from 1 to 6'
    )
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "string", "alphabet": ""}, "s.json")
    assert caught.value.message == (
        'schemamask: s.json: $: "alphabet" must be 1 to 16 distinct printable ASCII '
        "characters without quote or backslash"
    )
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "string", "alphabet": "aa"}, "s.json")
    assert caught.value.message == (
        'schemamask: s.json: $: "alphabet" must be 1 to 16 distinct printable ASCII '
        "characters without quote or backslash"
    )
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "string", "minLength": 3, "maxLength": 2}, "s.json")
    assert caught.value.message == ('schemamask: s.json: $: "minLength" is larger than "maxLength"')
    with pytest.raises(CliError) as caught:
        parse_schema({"type": "string", "maxLength": 17}, "s.json")
    assert caught.value.message == (
        'schemamask: s.json: $: "maxLength" must be an integer from 0 to 16'
    )
