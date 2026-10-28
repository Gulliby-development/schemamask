"""Tests for immutable model scripts."""

import pytest

from schemamask.errors import CliError
from schemamask.script import Script, load_script


def test_loads_scripts() -> None:
    assert load_script(b'{"steps":[[1,2],[0]],"fallback":"highest"}', "x.json", 3) == Script(
        ((1, 2), (0,)), "highest"
    )
    assert load_script(b"{}", "x.json", 3) == Script((), "lowest")


def test_rejects_bad_scripts() -> None:
    with pytest.raises(CliError) as caught:
        load_script(b"[]", "x.json", 3)
    assert caught.value.message == "schemamask: x.json: must be an object"

    with pytest.raises(CliError) as caught:
        load_script(b'{"x":1}', "x.json", 3)
    assert caught.value.message == 'schemamask: x.json: unknown keyword "x"'

    with pytest.raises(CliError) as caught:
        load_script(b'{"steps":[1]}', "x.json", 3)
    assert caught.value.message == (
        'schemamask: x.json: "steps" must be an array of arrays of up to 16 token ids'
    )

    with pytest.raises(CliError) as caught:
        load_script(b'{"steps":[[true]]}', "x.json", 3)
    assert caught.value.message == (
        'schemamask: x.json: "steps" must be an array of arrays of up to 16 token ids'
    )
