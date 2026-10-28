"""Prescribed vocabulary validation tests."""

import pytest

from schemamask.errors import CliError
from schemamask.vocab import Vocab, load_vocab


def test_loads_tokens() -> None:
    assert load_vocab(b'["a","<eos>","\\"x"]', "v.json") == Vocab(("a", "<eos>", '"x'))
    assert load_vocab(b'["{"]', "v.json") == Vocab(("{",))


def test_knows_the_end_token() -> None:
    assert Vocab(("a", "<eos>")).is_eos(1) is True
    assert Vocab(("a", "<eos>")).is_eos(0) is False


def test_rejects_bad_vocabularies() -> None:
    with pytest.raises(CliError) as caught:
        load_vocab(b"[]", "v.json")
    assert caught.value.message == "schemamask: v.json: must be an array of 1 to 4096 strings"

    with pytest.raises(CliError) as caught:
        load_vocab(b"{}", "v.json")
    assert caught.value.message == "schemamask: v.json: must be an array of 1 to 4096 strings"

    with pytest.raises(CliError) as caught:
        load_vocab(b"[1]", "v.json")
    assert (
        caught.value.message
        == "schemamask: v.json: token 0 is not 1 or more printable ASCII characters"
    )

    with pytest.raises(CliError) as caught:
        load_vocab(b'[""]', "v.json")
    assert (
        caught.value.message
        == "schemamask: v.json: token 0 is not 1 or more printable ASCII characters"
    )
