import pytest

from schemamask.errors import CliError
from schemamask.textio import decode_text, load_json


def test_decode_text_reads_valid_utf8() -> None:
    assert decode_text(b"ab", "s.json") == "ab"
    assert decode_text(b"", "s.json") == ""
    assert decode_text(b"\xef\xbb\xbfab", "s.json") == "ab"
    assert decode_text(b"\xef\xbb\xbf\xef\xbb\xbfab", "s.json") == "\ufeffab"


def test_decode_text_rejects_invalid_utf8() -> None:
    with pytest.raises(CliError) as caught:
        decode_text(b"\xff", "s.json")
    assert caught.value.message == "schemamask: s.json: input is not valid UTF-8"
    with pytest.raises(CliError) as caught:
        decode_text(b"\xc0\xaf", "s.json")
    assert caught.value.message == "schemamask: s.json: input is not valid UTF-8"


def test_load_json_reads_json() -> None:
    assert load_json(b'{"a":[1,"x",null,true]}', "s.json") == {"a": [1, "x", None, True]}
    assert load_json(b"\xef\xbb\xbf[1]", "s.json") == [1]


def test_load_json_rejects_bad_json() -> None:
    with pytest.raises(CliError) as caught:
        load_json(b"{", "s.json")
    assert caught.value.message == "schemamask: s.json: not valid JSON"
    with pytest.raises(CliError) as caught:
        load_json(b"", "s.json")
    assert caught.value.message == "schemamask: s.json: not valid JSON"
    with pytest.raises(CliError) as caught:
        load_json(b"NaN", "s.json")
    assert caught.value.message == "schemamask: s.json: not valid JSON"
