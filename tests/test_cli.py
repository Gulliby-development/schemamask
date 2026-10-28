from schemamask.cli import Result, run
from tests.files import read


def test_prints_help_and_usage() -> None:
    assert run(["help"], b"", read) == Result(
        0,
        (
            "usage: schemamask COMMAND [ARGS]\n"
            "  check SCHEMA\n"
            "  allowed SCHEMA VOCAB [--prefix TEXT]\n"
            "  decode SCHEMA VOCAB SCRIPT [--max-steps N] [--no-mask]\n"
            "  validate SCHEMA TEXT\n"
        ),
        "",
    )
    assert run(["-h"], b"", read) == Result(
        0,
        (
            "usage: schemamask COMMAND [ARGS]\n"
            "  check SCHEMA\n"
            "  allowed SCHEMA VOCAB [--prefix TEXT]\n"
            "  decode SCHEMA VOCAB SCRIPT [--max-steps N] [--no-mask]\n"
            "  validate SCHEMA TEXT\n"
        ),
        "",
    )
    assert run([], b"", read) == Result(
        2,
        "",
        (
            "usage: schemamask COMMAND [ARGS]\n"
            "  check SCHEMA\n"
            "  allowed SCHEMA VOCAB [--prefix TEXT]\n"
            "  decode SCHEMA VOCAB SCRIPT [--max-steps N] [--no-mask]\n"
            "  validate SCHEMA TEXT\n"
        ),
    )
    assert run(["frob"], b"", read) == Result(
        2,
        "",
        'schemamask: unknown command "frob"\n',
    )


def test_accepts_long_help_alias() -> None:
    assert run(["--help"], b"", read) == Result(
        0,
        (
            "usage: schemamask COMMAND [ARGS]\n"
            "  check SCHEMA\n"
            "  allowed SCHEMA VOCAB [--prefix TEXT]\n"
            "  decode SCHEMA VOCAB SCRIPT [--max-steps N] [--no-mask]\n"
            "  validate SCHEMA TEXT\n"
        ),
        "",
    )


def test_dispatches_every_command() -> None:
    assert run(["check", "flag.json"], b"", read) == Result(
        0, "ok\nshortest: true\nlongest: 5\n", ""
    )
    assert run(["validate", "pair.json", "doc.txt"], b"", read) == Result(0, "valid\n", "")
