from schemamask.nfa import Nfa


def advance(nfa: Nfa, states: frozenset[int], text: str) -> frozenset[int]:
    for char in text:
        states = nfa.step(states, char)
        if not states:
            return states
    return states


def prefix_states(nfa: Nfa, prefix: str) -> frozenset[int]:
    return advance(nfa, nfa.first(), prefix)


def complete(nfa: Nfa, text: str) -> bool:
    return nfa.accepts(advance(nfa, nfa.first(), text))


def dead_offset(nfa: Nfa, text: str) -> int | None:
    states = nfa.first()
    for offset, char in enumerate(text):
        states = nfa.step(states, char)
        if not states:
            return offset
    return None
