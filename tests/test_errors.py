from schemamask.errors import CliError


def test_default_code_is_two() -> None:
    assert CliError("x").code == 2
    assert CliError("x").message == "x"
    assert CliError("x", 1).code == 1
