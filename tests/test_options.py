import pytest

from schemamask.errors import CliError
from schemamask.options import Parsed, bounded, need, split


def test_splits_options_and_positionals() -> None:
    assert split(["a", "b"], {}) == Parsed(["a", "b"], {})
    assert split(["--prefix", "x", "s"], {"--prefix": True}) == Parsed(["s"], {"--prefix": "x"})
    assert split(["s", "--prefix="], {"--prefix": True}) == Parsed(["s"], {"--prefix": ""})
    assert split(["--no-mask", "s"], {"--no-mask": False}) == Parsed(["s"], {"--no-mask": ""})
    assert split(["-", "x"], {}) == Parsed(["-", "x"], {})


def test_rejects_bad_options() -> None:
    with pytest.raises(CliError) as caught:
        split(["--bogus"], {})
    assert caught.value.message == 'schemamask: unknown option "--bogus"'
    with pytest.raises(CliError) as caught:
        split(["-x"], {})
    assert caught.value.message == 'schemamask: unknown option "-x"'
    with pytest.raises(CliError) as caught:
        split(["--prefix"], {"--prefix": True})
    assert caught.value.message == "schemamask: option --prefix needs a value"
    with pytest.raises(CliError) as caught:
        split(["--no-mask=1"], {"--no-mask": False})
    assert caught.value.message == "schemamask: option --no-mask takes no value"


def test_bounds_numbers() -> None:
    assert bounded("1", "--max-steps", 400) == 1
    assert bounded("400", "--max-steps", 400) == 400
    assert bounded("007", "--max-steps", 400) == 7
    with pytest.raises(CliError) as caught:
        bounded("0", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "0": expected an integer from 1 to 400'
    )
    with pytest.raises(CliError) as caught:
        bounded("401", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "401": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("+1", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "+1": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("-1", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "-1": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded(" 1", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value " 1": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("1 ", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "1 ": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("\uff11", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "\uff11": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("\u0661", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "\u0661": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2
    with pytest.raises(CliError) as caught:
        bounded("0001", "--max-steps", 400)
    assert (
        caught.value.message
        == 'schemamask: bad --max-steps value "0001": expected an integer from 1 to 400'
    )
    assert caught.value.code == 2


def test_checks_argument_counts() -> None:
    with pytest.raises(CliError) as caught:
        need(Parsed(["a"], {}), 2, 2, "validate")
    assert caught.value.message == "schemamask: validate: wrong number of arguments"
    with pytest.raises(CliError) as caught:
        need(Parsed(["-", "-"], {}), 2, 2, "validate")
    assert caught.value.message == "schemamask: standard input can be read once"
    assert need(Parsed(["a", "b"], {}), 2, 2, "validate") is None
