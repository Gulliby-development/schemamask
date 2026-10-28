"""Tests for masked and unmasked deterministic decoding."""

from schemamask.build import compile_node
from schemamask.decode import Decoding, Step, decode
from schemamask.schema import Const
from schemamask.script import Script
from schemamask.vocab import Vocab


def test_decodes_under_the_mask() -> None:
    assert decode(
        compile_node(Const(("true", "false"))),
        Vocab(("t", "r", "u", "e", "f", "a", "l", "s", "<eos>")),
        Script(((8, 0),), "lowest"),
        max_steps=40,
        mask=True,
    ) == Decoding(
        (Step(1, 0, 7), Step(2, 1, 8), Step(3, 2, 8), Step(4, 3, 8), Step(5, 8, 8)),
        "true",
        "complete",
        valid=True,
    )
    assert decode(
        compile_node(Const(("true", "false"))),
        Vocab(("t", "r", "u", "e", "f", "a", "l", "s", "<eos>")),
        Script(((8, 0),), "lowest"),
        max_steps=40,
        mask=False,
    ) == Decoding((Step(1, 8, 0),), "", "complete", valid=False)


def test_stops_at_the_limit_or_when_stuck() -> None:
    assert decode(
        compile_node(Const(("true", "false"))),
        Vocab(("t", "r", "u", "e", "f", "a", "l", "s", "<eos>")),
        Script((), "highest"),
        max_steps=40,
        mask=True,
    ) == Decoding(
        (Step(1, 4, 7), Step(2, 5, 8), Step(3, 6, 8), Step(4, 7, 8), Step(5, 3, 8), Step(6, 8, 8)),
        "false",
        "complete",
        valid=True,
    )
    assert decode(
        compile_node(Const(("true", "false"))),
        Vocab(("t", "r", "u", "e", "f", "a", "l", "s", "<eos>")),
        Script(((4,),), "lowest"),
        max_steps=40,
        mask=True,
    ) == Decoding(
        (Step(1, 4, 7), Step(2, 5, 8), Step(3, 6, 8), Step(4, 7, 8), Step(5, 3, 8), Step(6, 8, 8)),
        "false",
        "complete",
        valid=True,
    )
