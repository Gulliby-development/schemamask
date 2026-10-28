import pytest

from schemamask.envio import Env
from schemamask.errors import CliError
from schemamask.walk import complete


def test_reads_files_and_standard_input() -> None:
    assert Env(b"in", lambda _: None).source("-") == (b"in", "<stdin>")
    assert Env(b"", lambda p: b"x" if p == "f" else None).source("f") == (b"x", "f")
    with pytest.raises(CliError) as caught:
        Env(b"", lambda _: None).source("missing.json")
    assert caught.value.message == "schemamask: missing.json: cannot read file"


def test_compiles_a_schema_file() -> None:
    assert complete(Env(b"", lambda _: b'{"type":"null"}').automaton("s.json"), "null") is True
    with pytest.raises(CliError) as caught:
        Env(b"", lambda _: b'{"type":"foo"}').automaton("s.json")
    assert caught.value.message == 'schemamask: s.json: $: unknown type "foo"'
    assert caught.value.code == 2
