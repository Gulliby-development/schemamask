"""Command adapter for listing vocabulary tokens allowed by a schema."""

from typing import TYPE_CHECKING

from schemamask.envio import Env
from schemamask.errors import CliError
from schemamask.mask import allowed_tokens

if TYPE_CHECKING:
    from schemamask.nfa import Nfa
from schemamask.options import need, split
from schemamask.render import allowed_lines
from schemamask.vocab import Vocab, load_vocab
from schemamask.walk import prefix_states

POSITIONAL_COUNT = 2


def run_allowed(args: list[str], env: Env) -> tuple[int, str]:
    """Return the allowed-token listing or raise a command-line input error."""
    parsed = split(args, {"--prefix": True})
    need(parsed, POSITIONAL_COUNT, POSITIONAL_COUNT, "allowed")

    schema_path, vocab_path = parsed.positionals
    nfa: Nfa = env.automaton(schema_path)
    data, label = env.source(vocab_path)
    vocab: Vocab = load_vocab(data, label)

    prefix = parsed.values.get("--prefix", "")
    states = prefix_states(nfa, prefix)
    if not states:
        message = "schemamask: prefix is not valid for the schema"
        raise CliError(message, 1)

    allowed = allowed_tokens(nfa, states, vocab)
    output = allowed_lines(vocab, allowed, complete=nfa.accepts(states))
    return (0 if allowed else 1), output
