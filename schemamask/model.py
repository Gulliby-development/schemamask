"""Deterministic preference selection for the fake model."""

from collections.abc import Sequence


def choose(wishes: Sequence[int], allowed: Sequence[int], fallback: str) -> int:
    """Return the first allowed wish, or the configured numeric extreme."""
    for wish in wishes:
        if wish in allowed:
            return wish

    if fallback == "lowest":
        return min(allowed)
    return max(allowed)
