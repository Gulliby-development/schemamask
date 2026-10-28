"""Injected source loading and schema automaton construction."""

from collections.abc import Callable
from dataclasses import dataclass

from schemamask.build import compile_node
from schemamask.errors import CliError
from schemamask.nfa import Nfa
from schemamask.schema import parse_schema
from schemamask.textio import load_json


@dataclass(frozen=True)
class Env:
    """An immutable execution environment for stdin and file reads."""

    stdin: bytes
    read: Callable[[str], bytes | None]

    def source(self, path: str) -> tuple[bytes, str]:
        """Return source bytes and their user-facing label."""
        if path == "-":
            return self.stdin, "<stdin>"

        data = self.read(path)
        if data is None:
            message = f"schemamask: {path}: cannot read file"
            raise CliError(message)
        return data, path

    def automaton(self, path: str) -> Nfa:
        """Load and compile the schema found at path."""
        data, label = self.source(path)
        value = load_json(data, label)
        node = parse_schema(value, label)
        return compile_node(node)
