from schemamask.cli import Result, run
from tests.files import read


def test_judges_a_document() -> None:
    assert run(["validate", "pair.json", "doc.txt"], b"", read) == Result(0, "valid\n", "")
    assert run(["validate", "pair.json", "nl.txt"], b"", read) == Result(0, "valid\n", "")
    assert run(["validate", "pair.json", "cut.txt"], b"", read) == Result(1, "incomplete\n", "")


def test_rejects_bad_input() -> None:
    assert run(["validate", "pair.json", "utf8bad.txt"], b"", read) == Result(
        2, "", "schemamask: utf8bad.txt: input is not valid UTF-8\n"
    )
    assert run(["validate", "pair.json", "gone.txt"], b"", read) == Result(
        2, "", "schemamask: gone.txt: cannot read file\n"
    )
    assert run(["validate", "-", "-"], b"", read) == Result(
        2, "", "schemamask: standard input can be read once\n"
    )


def test_reads_standard_input() -> None:
    assert run(["validate", "pair.json", "-"], b'{"id":0,"ok":false}', read) == Result(
        0, "valid\n", ""
    )
    assert run(
        ["validate", "-", "doc.txt"],
        b'{"type":"object","properties":{"id":{"type":"integer","maxDigits":1},"ok":{"type":"boolean"}}}',
        read,
    ) == Result(0, "valid\n", "")
