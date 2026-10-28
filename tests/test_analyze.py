"""Prescribed checks for shortest and longest automaton analysis."""

from schemamask.analyze import longest, shortest
from schemamask.build import compile_node
from schemamask.schema import Chars, Const, Digits


def test_finds_the_shortest_document() -> None:
    assert shortest(compile_node(Const(("true", "false")))) == "true"
    assert shortest(compile_node(Digits(2))) == "0"
    assert shortest(compile_node(Chars("ab", 1, 2))) == '"a"'


def test_finds_the_longest_length() -> None:
    assert longest(compile_node(Const(("true", "false")))) == 5
    assert longest(compile_node(Digits(2))) == 3
    assert longest(compile_node(Chars("ab", 1, 2))) == 4
