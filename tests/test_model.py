"""Tests for deterministic preference selection."""

from schemamask.model import choose


def test_takes_the_first_allowed_wish() -> None:
    assert choose([5, 2, 7], [1, 2, 7], "lowest") == 2
    assert choose([9], [1, 4], "lowest") == 1
    assert choose([9], [1, 4], "highest") == 4
    assert choose([], [3], "highest") == 3
