"""Implement the check command adapter."""

from schemamask.analyze import longest, shortest
from schemamask.envio import Env
from schemamask.options import need, split


def run_check(args: list[str], env: Env) -> tuple[int, str]:
    """Analyze the schema passed to the check command."""
    parsed = split(args, {})
    need(parsed, 1, 1, "check")
    nfa = env.automaton(parsed.positionals[0])
    output = f"ok\nshortest: {shortest(nfa)}\nlongest: {longest(nfa)}\n"
    return 0, output
