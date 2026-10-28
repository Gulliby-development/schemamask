from schemamask.build import compile_node
from schemamask.mask import allowed_tokens
from schemamask.schema import Const, Digits, Record
from schemamask.vocab import Vocab
from schemamask.walk import prefix_states


def test_masks_the_vocabulary_by_prefix() -> None:
    assert allowed_tokens(
        compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
        prefix_states(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            "",
        ),
        Vocab(
            (
                "{",
                "}",
                "[",
                "]",
                ",",
                ":",
                '"',
                '"id":',
                '"ok":',
                "true",
                "false",
                "null",
                "0",
                "1",
                "-",
                "a",
                "b",
                '"a',
                "<eos>",
            )
        ),
    ) == [0]
    assert allowed_tokens(
        compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
        prefix_states(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            "{",
        ),
        Vocab(
            (
                "{",
                "}",
                "[",
                "]",
                ",",
                ":",
                '"',
                '"id":',
                '"ok":',
                "true",
                "false",
                "null",
                "0",
                "1",
                "-",
                "a",
                "b",
                '"a',
                "<eos>",
            )
        ),
    ) == [6, 7]
    assert allowed_tokens(
        compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
        prefix_states(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            '{"id":',
        ),
        Vocab(
            (
                "{",
                "}",
                "[",
                "]",
                ",",
                ":",
                '"',
                '"id":',
                '"ok":',
                "true",
                "false",
                "null",
                "0",
                "1",
                "-",
                "a",
                "b",
                '"a',
                "<eos>",
            )
        ),
    ) == [12, 13, 14]
    assert allowed_tokens(
        compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
        prefix_states(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            '{"id":3',
        ),
        Vocab(
            (
                "{",
                "}",
                "[",
                "]",
                ",",
                ":",
                '"',
                '"id":',
                '"ok":',
                "true",
                "false",
                "null",
                "0",
                "1",
                "-",
                "a",
                "b",
                '"a',
                "<eos>",
            )
        ),
    ) == [4]
    assert (
        allowed_tokens(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            prefix_states(
                compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
                '{"id":3,"ok":tr',
            ),
            Vocab(
                (
                    "{",
                    "}",
                    "[",
                    "]",
                    ",",
                    ":",
                    '"',
                    '"id":',
                    '"ok":',
                    "true",
                    "false",
                    "null",
                    "0",
                    "1",
                    "-",
                    "a",
                    "b",
                    '"a',
                    "<eos>",
                )
            ),
        )
        == []
    )
