"""Compile schema nodes into deterministic acyclic NFAs."""

from schemamask.nfa import Nfa
from schemamask.schema import Chars, Const, Digits, Node, Record, Seq

DIGITS = "0123456789"
NONZERO_DIGITS = "123456789"
QUOTE = '"'


def compile_node(node: Node) -> Nfa:
    """Compile a node to an NFA using fresh, bounded Thompson fragments."""
    nfa = Nfa([], 0, 0)
    start, accept = _fragment(nfa, node)
    nfa.start = start
    nfa.accept = accept
    return nfa


def _fragment(nfa: Nfa, node: Node) -> tuple[int, int]:
    if isinstance(node, Const):
        return _literal_choice(nfa, node.texts)
    if isinstance(node, Digits):
        return _digits_fragment(nfa, node)
    if isinstance(node, Chars):
        return _chars_fragment(nfa, node)
    if isinstance(node, Seq):
        return _sequence_fragment(nfa, node)
    if isinstance(node, Record):
        return _record_fragment(nfa, node)
    return _choice_fragment(nfa, node.options)


def _literal_fragment(nfa: Nfa, text: str) -> tuple[int, int]:
    start = nfa.state()
    cursor = start
    for character in text:
        target = nfa.state()
        nfa.edge(cursor, character, target)
        cursor = target
    return start, cursor


def _literal_choice(nfa: Nfa, texts: tuple[str, ...]) -> tuple[int, int]:
    start = nfa.state()
    accept = nfa.state()
    for text in texts:
        branch_start, branch_accept = _literal_fragment(nfa, text)
        nfa.edge(start, None, branch_start)
        nfa.edge(branch_accept, None, accept)
    return start, accept


def _digits_fragment(nfa: Nfa, node: Digits) -> tuple[int, int]:
    start = nfa.state()
    signed = nfa.state()
    first_digit = nfa.state()
    accept = nfa.state()

    nfa.edge(start, "0", accept)
    nfa.edge(start, "-", signed)
    for digit in NONZERO_DIGITS:
        nfa.edge(start, digit, first_digit)
        nfa.edge(signed, digit, first_digit)

    current = first_digit
    nfa.edge(current, None, accept)
    for _ in range(1, node.count):
        following = nfa.state()
        for digit in DIGITS:
            nfa.edge(current, digit, following)
        current = following
        nfa.edge(current, None, accept)
    return start, accept


def _chars_fragment(nfa: Nfa, node: Chars) -> tuple[int, int]:
    start = nfa.state()
    accept = nfa.state()
    levels = [nfa.state() for _ in range(node.high + 1)]
    nfa.edge(start, QUOTE, levels[0])

    for length, level in enumerate(levels):
        if length >= node.low:
            nfa.edge(level, QUOTE, accept)
        if length < node.high:
            following = levels[length + 1]
            for character in node.alphabet:
                nfa.edge(level, character, following)
    return start, accept


def _sequence_fragment(nfa: Nfa, node: Seq) -> tuple[int, int]:
    start = nfa.state()
    accept = nfa.state()
    levels = [nfa.state() for _ in range(node.high + 1)]
    nfa.edge(start, "[", levels[0])

    for count, level in enumerate(levels):
        if count >= node.low:
            nfa.edge(level, "]", accept)
        if count < node.high:
            item_start, item_accept = _fragment(nfa, node.item)
            separator = "," if count > 0 else None
            nfa.edge(level, separator, item_start)
            following = levels[count + 1]
            nfa.edge(item_accept, None, following)
    return start, accept


def _append_literal(nfa: Nfa, source: int, text: str) -> int:
    cursor = source
    for character in text:
        target = nfa.state()
        nfa.edge(cursor, character, target)
        cursor = target
    return cursor


def _record_fragment(nfa: Nfa, node: Record) -> tuple[int, int]:
    start = nfa.state()
    cursor = _append_literal(nfa, start, "{")

    for index, (name, child) in enumerate(zip(node.names, node.nodes, strict=True)):
        if index > 0:
            cursor = _append_literal(nfa, cursor, ",")
        cursor = _append_literal(nfa, cursor, f'"{name}":')
        child_start, child_accept = _fragment(nfa, child)
        nfa.edge(cursor, None, child_start)
        following = nfa.state()
        nfa.edge(child_accept, None, following)
        cursor = following

    accept = _append_literal(nfa, cursor, "}")
    return start, accept


def _choice_fragment(nfa: Nfa, options: tuple[Node, ...]) -> tuple[int, int]:
    start = nfa.state()
    accept = nfa.state()
    for option in options:
        branch_start, branch_accept = _fragment(nfa, option)
        nfa.edge(start, None, branch_start)
        nfa.edge(branch_accept, None, accept)
    return start, accept
