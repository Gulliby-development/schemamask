from schemamask.envio import Env
from schemamask.options import need, split
from schemamask.textio import decode_text
from schemamask.walk import complete, dead_offset


def run_validate(args: list[str], env: Env) -> tuple[int, str]:
    """Validate a document source against a compiled schema."""
    parsed = split(args, {})
    need(parsed, 2, 2, "validate")
    schema_path, text_path = parsed.positionals

    nfa = env.automaton(schema_path)
    data, label = env.source(text_path)
    text = decode_text(data, label).removesuffix("\n")

    offset = dead_offset(nfa, text)
    if offset is not None:
        return 1, f"invalid at {offset}\n"
    if complete(nfa, text):
        return 0, "valid\n"
    return 1, "incomplete\n"
