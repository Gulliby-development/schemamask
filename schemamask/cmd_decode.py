"""Command adapter for scripted decoding."""

from schemamask.decode import decode
from schemamask.envio import Env
from schemamask.options import bounded, need, split
from schemamask.render import brief_lines, decoding_lines
from schemamask.script import load_script
from schemamask.vocab import load_vocab

DEFAULT_MAX_STEPS = 40
MAX_STEPS = 400


def run_decode(args: list[str], env: Env) -> tuple[int, str]:
    """Load command inputs and run a scripted decoding session."""
    parsed = split(args, {"--max-steps": True, "--no-mask": False, "--brief": False})
    need(parsed, 3, 3, "decode")
    max_steps = DEFAULT_MAX_STEPS
    if "--max-steps" in parsed.values:
        max_steps = bounded(parsed.values["--max-steps"], "--max-steps", MAX_STEPS)

    schema_path, vocab_path, script_path = parsed.positionals
    automaton = env.automaton(schema_path)
    vocab_data, vocab_label = env.source(vocab_path)
    vocab = load_vocab(vocab_data, vocab_label)
    script_data, script_label = env.source(script_path)
    script = load_script(script_data, script_label, len(vocab.tokens))

    decoding = decode(
        automaton,
        vocab,
        script,
        max_steps=max_steps,
        mask="--no-mask" not in parsed.values,
    )
    if "--brief" in parsed.values:
        output = brief_lines(decoding)
    else:
        output = decoding_lines(vocab, decoding)
    exit_code = 0 if decoding.status == "complete" and decoding.valid else 1
    return exit_code, output
