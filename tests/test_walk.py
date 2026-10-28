from schemamask.build import compile_node
from schemamask.schema import Const, Digits, Record
from schemamask.walk import dead_offset, prefix_states


def test_prefix_states_is_empty_when_no_document_starts_with_the_text() -> None:
    assert (
        bool(
            prefix_states(
                compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
                '{"id":3,"o',
            )
        )
        is True
    )
    assert (
        bool(
            prefix_states(
                compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
                '{"id":x',
            )
        )
        is False
    )
    assert (
        bool(
            prefix_states(
                compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
                "",
            )
        )
        is True
    )


def test_dead_offset_names_the_first_bad_character() -> None:
    assert (
        dead_offset(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            '{"id":x',
        )
        == 6
    )
    assert (
        dead_offset(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            '{"id":3,"ok":true}',
        )
        is None
    )
    assert (
        dead_offset(
            compile_node(Record(("id", "ok"), (Digits(1), Const(("true", "false"))))),
            "x",
        )
        == 0
    )
    assert dead_offset(compile_node(Digits(2)), "-12") is None
    assert dead_offset(compile_node(Digits(2)), "-123") == 3
