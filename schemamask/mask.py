from schemamask.nfa import Nfa
from schemamask.vocab import Vocab
from schemamask.walk import advance


def allowed_tokens(nfa: Nfa, states: frozenset[int], vocab: Vocab) -> list[int]:
    """Return vocabulary IDs whose complete tokens preserve a valid prefix."""
    allowed: list[int] = []
    for token_id, token in enumerate(vocab.tokens):
        if vocab.is_eos(token_id):
            if nfa.accepts(states):
                allowed.append(token_id)
        elif states and advance(nfa, states, token):
            allowed.append(token_id)
    return allowed
