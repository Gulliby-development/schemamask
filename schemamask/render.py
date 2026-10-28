"""Pure text renderers for tokens, masks, and decoding results."""

import json

from schemamask.decode import Decoding
from schemamask.vocab import EOS, Vocab


def token_text(token: str) -> str:
    """Render EOS bare and ordinary vocabulary tokens as JSON strings."""
    if token == EOS:
        return EOS
    return json.dumps(token)


def allowed_lines(vocab: Vocab, allowed: list[int], *, complete: bool) -> str:
    """Render an allowed-token listing in the supplied ID order."""
    state = "complete" if complete else "open"
    lines = [f"state: {state}", f"allowed: {len(allowed)} of {len(vocab.tokens)}"]
    lines.extend(f"{token_id} {token_text(vocab.tokens[token_id])}" for token_id in allowed)
    return "\n".join(lines) + "\n"


def decoding_lines(vocab: Vocab, decoding: Decoding) -> str:
    """Render every recorded decoding step followed by its final result."""
    lines = [
        f"{step.number} {step.token} {token_text(vocab.tokens[step.token])} masked={step.masked}"
        for step in decoding.steps
    ]
    valid = "yes" if decoding.valid else "no"
    lines.extend(
        (
            f"text: {decoding.text}",
            f"status: {decoding.status}",
            f"valid: {valid}",
        )
    )
    return "\n".join(lines) + "\n"
