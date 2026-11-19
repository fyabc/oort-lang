#! /usr/bin/env python

"""End-to-end tests for the JSON CLI example."""

from pathlib import Path

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import EXAMPLES_DIR, get_compiler

EXAMPLE = EXAMPLES_DIR / "07_showcase" / "07_00_json.ort"
SAMPLE = EXAMPLES_DIR / "07_showcase" / "sample.json"


def _run_example(path: Path):
    return get_compiler([str(EXAMPLE), str(path)]).run_file(EXAMPLE)


def test_json_example_parses_file(capsys):
    _run_example(SAMPLE)
    out = capsys.readouterr().out
    assert '"project": "Oort"' in out
    assert '"frontend": "ANTLR + Pratt"' in out
    assert '"unicode": "你好"' in out


def test_json_example_reports_invalid_json(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"a": [1, 2,]}', encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        _run_example(bad)
    assert exc_info.value.code == 1
    assert "JSON error: unexpected character ']'" in capsys.readouterr().out


def test_json_example_missing_file_is_a_runtime_error(tmp_path, caplog):
    missing = tmp_path / "missing.json"
    with pytest.raises(CompilerError):
        _run_example(missing)
    assert "No such file or directory" in caplog.text


def _write_text(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "input.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_json_example_escapes_numbers_and_surrogates(tmp_path, capsys):
    path = _write_text(
        tmp_path,
        r'{"esc": "a\"b\\c\n\t", "num": -1.5e+2, "u": "你😀"}',
    )
    _run_example(path)
    out = capsys.readouterr().out
    assert '"num": -150.0' in out
    assert '"u": "你😀"' in out
    assert r'"esc": "a\"b\\c\n\t"' in out


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (r'{"a": "\x"}', "invalid escape"),
        (r'{"a": "\uD800"}', "unpaired high surrogate"),
        (r'{"a": "\uDC00"}', "unpaired low surrogate"),
        ('{"a": 1} extra', "trailing data"),
        ('{"a": [1, 2,]}', "unexpected character ']'"),
    ],
)
def test_json_example_rejects_invalid_input(tmp_path, capsys, text: str, message: str):
    path = _write_text(tmp_path, text)
    with pytest.raises(SystemExit) as exc_info:
        _run_example(path)
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "JSON error:" in out
    assert message in out
