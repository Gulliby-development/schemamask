"""Vocabulary loading and token identity helpers."""

from dataclasses import dataclass

from schemamask.errors import CliError
from schemamask.textio import load_json

EOS = "<eos>"
MIN_TOKENS = 1
MAX_TOKENS = 4096
MIN_TOKEN_ID = 0
MIN_PRINTABLE = 32
MAX_PRINTABLE = 126


@dataclass(frozen=True)
class Vocab:
    """An ordered, immutable sequence of model tokens."""

    tokens: tuple[str, ...]

    def is_eos(self, token_id: int) -> bool:
        """Return whether a valid token ID names the exact end token."""
        if isinstance(token_id, bool) or not MIN_TOKEN_ID <= token_id < len(self.tokens):
            return False
        return self.tokens[token_id] == EOS


def load_vocab(data: bytes, label: str) -> Vocab:
    """Load and validate an ordered vocabulary from strict JSON bytes."""
    value = load_json(data, label)
    if not isinstance(value, list) or not MIN_TOKENS <= len(value) <= MAX_TOKENS:
        message = f"schemamask: {label}: must be an array of 1 to 4096 strings"
        raise CliError(message)

    tokens: list[str] = []
    seen: set[str] = set()
    for token_id, token in enumerate(value):
        if (
            not isinstance(token, str)
            or not token
            or not all(MIN_PRINTABLE <= ord(character) <= MAX_PRINTABLE for character in token)
        ):
            message = (
                f"schemamask: {label}: token {token_id} is not 1 or more printable ASCII characters"
            )
            raise CliError(message)
        if token in seen:
            message = f"schemamask: {label}: token {token_id} is a duplicate"
            raise CliError(message)
        tokens.append(token)
        seen.add(token)

    return Vocab(tuple(tokens))
