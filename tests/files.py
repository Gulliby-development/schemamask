"""Shared fixture files: every test reads them through read()."""

FILES: dict[str, bytes] = {
    "flag.json": b'{"type":"boolean"}',
    "pair.json": (
        b'{"type":"object","properties":{"id":{"ty'
        b'pe":"integer","maxDigits":1},"ok":{"type'
        b'":"boolean"}}}'
    ),
    "tags.json": (b'{"type":"array","items":{"enum":["a","b"]},"minItems":1,"maxItems":2}'),
    "either.json": (b'{"anyOf":[{"type":"null"},{"type":"string","alphabet":"ab","maxLength":2}]}'),
    "bad.json": b'{"type":"foo"}',
    "words.json": (
        b'["{","}","[","]",",",":","\\"","\\"id\\":",'
        b'"\\"ok\\":","true","false","null","0","1",'
        b'"-","a","b","\\"a","<eos>"]'
    ),
    "tiny.json": (b'["t","r","u","e","f","a","l","s","<eos>"]'),
    "chatty.json": (b'{"steps":[[15,16],[15],[16]],"fallback":"lowest"}'),
    "greedy.json": (b'{"steps":[[9],[10]],"fallback":"highest"}'),
    "spell.json": b'{"steps":[[0],[1],[2],[3],[4],[8]]}',
    "badscript.json": b'{"steps": [[0, 99]]}',
    "doc.txt": b'{"id":3,"ok":true}',
    "cut.txt": b'{"id":3,"o',
    "wrong.txt": b'{"id":33}',
    "nl.txt": b'{"id":-7,"ok":false}\n',
    "utf8bad.txt": b"\xff",
}


def read(path: str) -> bytes | None:
    return FILES.get(path)
