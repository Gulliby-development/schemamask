from schemamask.build import compile_node
from schemamask.schema import Chars, Const, Digits, Seq
from schemamask.walk import complete


def test_accepts_exactly_the_documents() -> None:
    assert complete(compile_node(Const(("true", "false"))), "true") is True
    assert complete(compile_node(Const(("true", "false"))), "false") is True
    assert complete(compile_node(Const(("true", "false"))), "tru") is False
    assert complete(compile_node(Digits(2)), "0") is True
    assert complete(compile_node(Digits(2)), "-12") is True
    assert complete(compile_node(Digits(2)), "99") is True
    assert complete(compile_node(Chars("ab", 1, 2)), '"a"') is True
    assert complete(compile_node(Chars("ab", 1, 2)), '"ab"') is True
    assert complete(compile_node(Chars("ab", 1, 2)), '""') is False
    assert complete(compile_node(Seq(Digits(1), 1, 2)), "[1]") is True
    assert complete(compile_node(Seq(Digits(1), 1, 2)), "[1,-2]") is True
    assert complete(compile_node(Seq(Digits(1), 1, 2)), "[]") is False
