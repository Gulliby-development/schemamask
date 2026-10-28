<p align="center"><img src="docs/logo.svg" width="96" alt="" /></p>

# schemamask

schemamask is a deterministic, offline demonstration of JSON-schema-constrained
decoding for people who build agents and other model-powered applications. It compiles a
small schema subset into an automaton, reports which vocabulary tokens keep a generated
text viable, validates text, and compares scripted decoding with and without that mask.
The “model” is a local preference script: there is no network call, API key, randomness,
or model dependency.

[![CI](https://github.com/Gulliby-development/schemamask/actions/workflows/ci.yml/badge.svg)](https://github.com/Gulliby-development/schemamask/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

The application requires Python 3.11 or newer and uses only the Python standard library
at runtime. It is run from a source checkout with `python -m schemamask`.

## Install

Clone this repository (`git clone https://github.com/Gulliby-development/schemamask.git`), then run commands from its root directory. No runtime
package installation is needed. Ensure Python 3.11+ is on your PATH; on Windows, the
Python launcher can be used as `py -3.11 -m schemamask` instead of `python -m schemamask`.
The commands below work on Windows, macOS, and Linux when invoked with the appropriate
Python executable.

For example, create and activate an isolated development environment:

```text
python -m venv .venv
```

Activate it with `.venv\Scripts\activate.bat` in Windows Command Prompt,
`.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` on
macOS/Linux. The application itself still runs offline and needs no third-party runtime
packages. To run the developer checks, install their optional tools into that environment:

```text
python -m pip install pytest ruff
```

## Quick start

The examples use files you create in the repository root. Save the following UTF-8
contents as `pair.json`, `words.json`, `chatty.json`, and `doc.txt`:

**pair.json** — an object with two required properties, in the listed order:

```json
{"type":"object","properties":{"id":{"type":"integer","maxDigits":1},"ok":{"type":"boolean"}}}
```

**words.json** — a vocabulary array; each array index is the token ID:

```json
["{","}","[","]",",",":","\"","\"id\":","\"ok\":","true","false","null","0","1","-","a","b","\"a","<eos>"]
```

**chatty.json** — the fake model's per-step preferred IDs:

```json
{"steps":[[15,16],[15],[16]],"fallback":"lowest"}
```

**doc.txt**:

```text
{"id":3,"ok":true}
```

Check the schema's shortest and longest documents:

```console
$ python -m schemamask check pair.json
ok
shortest: {"id":0,"ok":true}
longest: 20
```

List tokens allowed after the complete document `true`. EOS is the only allowed token:

```console
$ python -m schemamask allowed flag.json words.json --prefix=true
state: complete
allowed: 1 of 19
18 <eos>
```

For that command, also create **flag.json** containing `{"type":"boolean"}`. A prefix
may be supplied as `--prefix TEXT` or `--prefix=TEXT`; omitting it means the empty
prefix. An open prefix with zero allowed tokens exits 1, as does a prefix that cannot
begin any document (the latter also reports an error).

Validate a text file:

```console
$ python -m schemamask validate pair.json doc.txt
valid
```

The validate command exits 0 for a complete valid document and 1 for an invalid or
incomplete one.

Decode the chatty preferences under the token mask:

```console
$ python -m schemamask decode pair.json words.json chatty.json
1 0 "{" masked=18
2 6 "\"" masked=17
text: {"
status: stuck
valid: no
```

This intentionally fails to complete: the script has no preferred tokens for the
required property name and the fallback token is not viable. Compare an unmasked run:

```console
$ python -m schemamask decode pair.json words.json chatty.json --no-mask --max-steps 4
1 15 "a" masked=0
2 15 "a" masked=0
3 16 "b" masked=0
4 0 "{" masked=0
text: aab{
status: stopped
valid: no
```

For a successful masked run, save **tiny.json** as
`["t","r","u","e","f","a","l","s","<eos>"]` and **spell.json** as
`{"steps":[[0],[1],[2],[3],[4],[8]]}`, then run:

```console
$ python -m schemamask decode flag.json tiny.json spell.json
1 0 "t" masked=7
2 1 "r" masked=8
3 2 "u" masked=8
4 3 "e" masked=8
5 8 <eos> masked=8
text: true
status: complete
valid: yes
```

A vocabulary is a JSON array of 1–4096 unique, nonempty printable ASCII token strings;
array indexes are token IDs. The reserved `<eos>` token may occur at most once and is
never added to the output text. A script is a JSON object with optional `steps` (default
empty) and `fallback` (default `lowest`, alternatively `highest`). Each step is a list of
up to 16 preferred token IDs, all within the vocabulary range. The fake model chooses
the first allowed preferred ID, then falls back to the lowest or highest allowed ID.

A mask consumes whole vocabulary tokens: every character in a token must preserve a
prefix of some valid document. EOS (`<eos>`) ends generation and is allowed only when
the current text is a complete document. The `masked=K` field counts vocabulary tokens
removed at that step; it is always zero for `--no-mask`. The fake model picks the first
preferred ID that is allowed, then falls back to the lowest or highest allowed ID as
configured. Unmasked decoding may pick any preferred ID, even one that produces invalid
text.

Decode status and validity are separate. `complete` means EOS was selected;
`stopped` means the step limit was reached; `stuck` means masking left no token to
select. Only `valid: yes` means the emitted text is a complete schema document. The
default limit is 40 steps; `--max-steps N` accepts values from 1 through 400.
Options may appear among positional arguments and use either `--name value` or
`--name=value` syntax. A path of `-` reads standard input, which can be consumed only
once per command.

## Supported schema subset

Schemas are JSON objects. Supported node kinds are:

- `{"type":"boolean"}` and `{"type":"null"}`: the literals `true`/`false` and
  `null`.
- `{"type":"integer","maxDigits":N}`: an optional minus followed by a nonzero digit
  and up to N−1 more digits, or `0`. N defaults to 3 and ranges from 1 to 6; `-0`
  and leading-zero forms are not documents.
- `{"type":"string","alphabet":A,"minLength":L,"maxLength":H}`: strings of L through
  H characters. Explicit alphabets contain 1–16 distinct printable ASCII characters,
  excluding quote and backslash. Length bounds default to 0 and 8 and range from 0 to
  16, with minimum no greater than maximum. If omitted, the lowercase alphabet is used;
  that built-in default is intentionally exempt from the explicit alphabet-size check.
- `{"enum":[...]}`: 1–8 distinct compact-JSON values. Strings contain 0–16 characters
  from the supported string alphabet; integers have absolute value below 1,000,000.
  Booleans and null are also allowed.
- `{"type":"array","items":S,"minItems":A,"maxItems":B}`: arrays of schemas S.
  Item counts default to 0–3, each bound ranges from 0 to 5, and the minimum cannot
  exceed the maximum.
- `{"type":"object","properties":{...}}`: up to six required properties, emitted in
  the exact order written in the schema; extra properties are not permitted. Names are
  1–16 lowercase ASCII letters or underscores. An empty properties object allows only
  `{}`.
- `{"anyOf":[S,...]}`: a choice among 2–4 schemas.

The subset recognizes only these keywords; it is not a general JSON Schema
implementation. Documents use compact JSON syntax, so whitespace outside supported
string contents is not accepted. Spaces are allowed inside strings when they belong to
the selected alphabet. Object property order is significant and every listed property
is required. General JSON Schema features such as optional properties, additional
properties, numeric ranges, references, and arbitrary validation keywords are not
supported.

Input files must be valid UTF-8. One leading UTF-8 BOM is ignored. JSON inputs reject
duplicate keys, non-finite numbers, malformed JSON, and trailing data. Validation drops
exactly one trailing LF from the document file; it does not strip CRLF as a pair.
Command errors are written to stderr and have exit code 2; valid command results exit 0,
and negative/incomplete command outcomes exit 1. See `python -m schemamask help` for
the command synopsis.

## Development

Run the checks from the repository root:

```text
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

The project keeps its test and lint configuration in `pyproject.toml`.

## License

MIT, see [LICENSE](LICENSE).

---

Built with BAKED
