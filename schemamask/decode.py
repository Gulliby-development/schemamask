from dataclasses import dataclass

from schemamask.mask import allowed_tokens
from schemamask.model import choose
from schemamask.nfa import Nfa
from schemamask.script import Script
from schemamask.vocab import Vocab
from schemamask.walk import advance, complete


@dataclass(frozen=True)
class Step:
    """One selected token and the number of vocabulary entries masked out."""

    number: int
    token: int
    masked: int


@dataclass(frozen=True)
class Decoding:
    """An immutable record of a scripted decoding run."""

    steps: tuple[Step, ...]
    text: str
    status: str
    valid: bool


def decode(
    nfa: Nfa,
    vocab: Vocab,
    script: Script,
    *,
    max_steps: int,
    mask: bool,
) -> Decoding:
    """Run the deterministic scripted model with or without token masking."""
    text = ""
    states = nfa.first()
    steps: list[Step] = []
    status = "stopped"

    for number in range(1, max_steps + 1):
        allowed = allowed_tokens(nfa, states, vocab) if mask else list(range(len(vocab.tokens)))
        if not allowed:
            status = "stuck"
            break

        wishes = script.steps[number - 1] if number <= len(script.steps) else ()
        token_id = choose(wishes, allowed, script.fallback)
        masked = len(vocab.tokens) - len(allowed) if mask else 0
        steps.append(Step(number, token_id, masked))

        if vocab.is_eos(token_id):
            status = "complete"
            break

        token = vocab.tokens[token_id]
        text += token
        states = advance(nfa, states, token)

    return Decoding(tuple(steps), text, status, complete(nfa, text))
