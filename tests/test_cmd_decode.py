from schemamask.cli import Result, run
from tests.files import read


def test_masks_a_chatty_model() -> None:
    assert run(["decode", "pair.json", "words.json", "chatty.json"], b"", read) == Result(
        1,
        ('1 0 "{" masked=18\n2 6 "\\"" masked=17\ntext: {"\nstatus: stuck\nvalid: no\n'),
        "",
    )
    assert run(["decode", "flag.json", "tiny.json", "greedy.json"], b"", read) == Result(
        2,
        "",
        'schemamask: greedy.json: "steps" holds an id outside the vocabulary\n',
    )


def test_shows_what_the_unmasked_model_does() -> None:
    assert run(
        ["decode", "pair.json", "words.json", "chatty.json", "--no-mask", "--max-steps", "4"],
        b"",
        read,
    ) == Result(
        1,
        (
            '1 15 "a" masked=0\n'
            '2 15 "a" masked=0\n'
            '3 16 "b" masked=0\n'
            '4 0 "{" masked=0\n'
            "text: aab{\n"
            "status: stopped\n"
            "valid: no\n"
        ),
        "",
    )
    assert run(
        ["decode", "pair.json", "words.json", "chatty.json", "--max-steps=3"],
        b"",
        read,
    ) == Result(
        1,
        ('1 0 "{" masked=18\n2 6 "\\"" masked=17\ntext: {"\nstatus: stuck\nvalid: no\n'),
        "",
    )


def test_rejects_bad_arguments() -> None:
    assert run(["decode", "pair.json", "words.json", "badscript.json"], b"", read) == Result(
        2,
        "",
        'schemamask: badscript.json: "steps" holds an id outside the vocabulary\n',
    )
    assert run(
        ["decode", "pair.json", "words.json", "chatty.json", "--max-steps", "0"],
        b"",
        read,
    ) == Result(
        2,
        "",
        'schemamask: bad --max-steps value "0": expected an integer from 1 to 400\n',
    )
    assert run(["decode", "pair.json", "words.json"], b"", read) == Result(
        2,
        "",
        "schemamask: decode: wrong number of arguments\n",
    )
