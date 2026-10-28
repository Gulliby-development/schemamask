"""Analyze accepted document lengths in an acyclic NFA."""

from collections import deque

from schemamask.nfa import Nfa


def _topological_order(nfa: Nfa) -> list[int]:
    """Return states in topological order using every graph edge."""
    indegrees = [0] * len(nfa.edges)
    for outgoing in nfa.edges:
        for _, target in outgoing:
            indegrees[target] += 1

    ready = deque(state for state, indegree in enumerate(indegrees) if indegree == 0)
    order: list[int] = []
    while ready:
        state = ready.popleft()
        order.append(state)
        for _, target in nfa.edges[state]:
            indegrees[target] -= 1
            if indegrees[target] == 0:
                ready.append(target)
    return order


def shortest(nfa: Nfa) -> str:
    """Return the shortest accepted text, breaking ties lexically."""
    best: list[str | None] = [None] * len(nfa.edges)
    for state in reversed(_topological_order(nfa)):
        choices: list[str] = []
        if state == nfa.accept:
            choices.append("")
        for char, target in nfa.edges[state]:
            suffix = best[target]
            if suffix is not None:
                choices.append(("" if char is None else char) + suffix)
        if choices:
            best[state] = min(choices, key=lambda text: (len(text), text))
    result = best[nfa.start]
    if result is None:
        return ""
    return result


def longest(nfa: Nfa) -> int:
    """Return the maximum accepted text length."""
    best: list[int | None] = [None] * len(nfa.edges)
    for state in reversed(_topological_order(nfa)):
        lengths: list[int] = []
        if state == nfa.accept:
            lengths.append(0)
        for char, target in nfa.edges[state]:
            suffix_length = best[target]
            if suffix_length is not None:
                lengths.append(suffix_length + (0 if char is None else 1))
        if lengths:
            best[state] = max(lengths)
    result = best[nfa.start]
    if result is None:
        return 0
    return result
