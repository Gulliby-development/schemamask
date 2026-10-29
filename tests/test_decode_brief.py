import pytest

from schemamask.cli import Result, run
from tests.files import read

PAIR = ["pair.json", "words.json", "chatty.json"]
SPELL = ["flag.json", "tiny.json", "spell.json"]
STUCK = Result(1, 'text: {"\nstatus: stuck\nvalid: no\nsteps: 2\nmasked: 35\n', "")
DONE = Result(0, "text: true\nstatus: complete\nvalid: yes\nsteps: 5\nmasked: 39\n", "")


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["decode", *PAIR, "--brief"], STUCK),
        (["decode", "--brief", *PAIR], STUCK),
        (["decode", *PAIR, "--brief", "--brief"], STUCK),
        (["decode", *PAIR, "--max-steps=3", "--brief"], STUCK),
        (["decode", *SPELL, "--brief"], DONE),
        (["decode", "--brief", *SPELL], DONE),
        (
            ["decode", *PAIR, "--no-mask", "--max-steps", "4", "--brief"],
            Result(1, "text: aab{\nstatus: stopped\nvalid: no\nsteps: 4\nmasked: 0\n", ""),
        ),
        (
            ["decode", *SPELL, "--max-steps", "2", "--brief"],
            Result(1, "text: tr\nstatus: stopped\nvalid: no\nsteps: 2\nmasked: 15\n", ""),
        ),
        (
            ["decode", *SPELL, "--no-mask", "--brief"],
            Result(1, "text: truef\nstatus: complete\nvalid: no\nsteps: 6\nmasked: 0\n", ""),
        ),
        (
            ["decode", *SPELL, "--brief=1"],
            Result(2, "", "schemamask: option --brief takes no value\n"),
        ),
        (
            ["decode", "flag.json", "tiny.json", "--brief"],
            Result(2, "", "schemamask: decode: wrong number of arguments\n"),
        ),
        (
            ["decode", "flag.json", "tiny.json", "greedy.json", "--brief"],
            Result(
                2,
                "",
                'schemamask: greedy.json: "steps" holds an id outside the vocabulary\n',
            ),
        ),
        (
            ["decode", *SPELL, "--brief", "--max-steps", "0"],
            Result(
                2,
                "",
                'schemamask: bad --max-steps value "0": expected an integer from 1 to 400\n',
            ),
        ),
    ],
)
def test_prints_only_the_result_and_the_totals(args: list[str], expected: Result) -> None:
    assert run(args, b"", read) == expected


def test_leaves_the_default_report_alone() -> None:
    result = run(["decode", *SPELL], b"", read)

    assert result.exit == 0
    assert result.out.startswith('1 0 "t" masked=7\n')
    assert "steps:" not in result.out
    assert "masked: " not in result.out
