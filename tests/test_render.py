"""Tests for exact token and decoding rendering."""

from schemamask.decode import Decoding, Step
from schemamask.render import allowed_lines, decoding_lines, token_text
from schemamask.vocab import Vocab


def test_shows_tokens() -> None:
    assert token_text("a") == '"a"'
    assert token_text('"') == '"\\""'
    assert token_text("<eos>") == "<eos>"


def test_lists_allowed_tokens() -> None:
    assert allowed_lines(Vocab(("a", "<eos>", "b")), [0, 1], complete=True) == (
        'state: complete\nallowed: 2 of 3\n0 "a"\n1 <eos>\n'
    )
    assert allowed_lines(Vocab(("a",)), [], complete=False) == "state: open\nallowed: 0 of 1\n"


def test_lists_decoding_steps() -> None:
    assert decoding_lines(
        Vocab(("a", "<eos>")),
        Decoding((Step(1, 0, 1), Step(2, 1, 0)), "a", "complete", valid=True),
    ) == ('1 0 "a" masked=1\n2 1 <eos> masked=0\ntext: a\nstatus: complete\nvalid: yes\n')
