from schemamask.cli import Result, run
from tests.files import read


def test_lists_the_allowed_tokens() -> None:
    assert run(["allowed", "pair.json", "words.json"], b"", read) == Result(
        0,
        'state: open\nallowed: 1 of 19\n0 "{"\n',
        "",
    )
    assert run(
        ["allowed", "flag.json", "words.json", "--prefix", "t"],
        b"",
        read,
    ) == Result(
        1,
        "state: open\nallowed: 0 of 19\n",
        "",
    )
    assert run(
        ["allowed", "flag.json", "words.json", "--prefix=true"],
        b"",
        read,
    ) == Result(
        0,
        "state: complete\nallowed: 1 of 19\n18 <eos>\n",
        "",
    )


def test_handles_edge_prefixes_and_bad_arguments() -> None:
    assert run(
        ["allowed", "flag.json", "words.json", "--prefix", "x"],
        b"",
        read,
    ) == Result(
        1,
        "",
        "schemamask: prefix is not valid for the schema\n",
    )
    assert run(
        ["allowed", "flag.json", "tiny.json", "--prefix"],
        b"",
        read,
    ) == Result(
        2,
        "",
        "schemamask: option --prefix needs a value\n",
    )
    assert run(["allowed", "pair.json"], b"", read) == Result(
        2,
        "",
        "schemamask: allowed: wrong number of arguments\n",
    )
    assert run(["allowed", "pair.json", "bad.json"], b"", read) == Result(
        2,
        "",
        "schemamask: bad.json: must be an array of 1 to 4096 strings\n",
    )
