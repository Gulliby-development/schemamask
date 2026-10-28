from schemamask.cli import Result, run
from tests.files import read


def test_prints_the_shortest_and_longest_document() -> None:
    assert run(["check", "flag.json"], b"", read) == Result(
        0,
        "ok\nshortest: true\nlongest: 5\n",
        "",
    )
    assert run(["check", "pair.json"], b"", read) == Result(
        0,
        'ok\nshortest: {"id":0,"ok":true}\nlongest: 20\n',
        "",
    )
    assert run(["check", "tags.json"], b"", read) == Result(
        0,
        'ok\nshortest: ["a"]\nlongest: 9\n',
        "",
    )
    assert run(["check", "either.json"], b"", read) == Result(
        0,
        'ok\nshortest: ""\nlongest: 4\n',
        "",
    )


def test_reports_problems() -> None:
    assert run(["check", "bad.json"], b"", read) == Result(
        2,
        "",
        'schemamask: bad.json: $: unknown type "foo"\n',
    )
    assert run(["check"], b"", read) == Result(
        2,
        "",
        "schemamask: check: wrong number of arguments\n",
    )
    assert run(["check", "missing.json"], b"", read) == Result(
        2,
        "",
        "schemamask: missing.json: cannot read file\n",
    )
    assert run(["check", "-"], b"\xff", read) == Result(
        2,
        "",
        "schemamask: <stdin>: input is not valid UTF-8\n",
    )
