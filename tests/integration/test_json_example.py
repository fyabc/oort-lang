#! /usr/bin/env python

"""End-to-end tests for the JSON CLI example."""

from pathlib import Path

import pytest

from oort_lang.diagnostics import OortException
from oort_lang.driver.compiler import CompilerError
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.source.input_info import FileInputInfo
from tests.helpers import EXAMPLES_DIR, get_compiler

EXAMPLE = EXAMPLES_DIR / "07_showcase" / "07_00_json.ort"
SAMPLE = EXAMPLES_DIR / "07_showcase" / "sample.json"

# Compiling the 380-line parser takes ~13s; keep it out of the default run.
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def compiled_example():
    """Compile the showcase once; each case re-executes it with new args."""
    compiler = get_compiler(["NOT_EXIST", "-t", "eval"])
    input_info = FileInputInfo(EXAMPLE)
    ast = compiler.compile_unit(input_info)
    assert ast is not None
    return compiler, ast, input_info


def _run_example(compiled_example, path: Path | None):
    compiler, ast, input_info = compiled_example
    interpreter = ASTInterpreter(compiler.error_handler)
    interpreter.script_args = () if path is None else (str(path),)
    interpreter.script_path = str(input_info.module_path)
    loader = compiler.make_module_loader(interpreter, input_info.module_dir)
    interpreter.module_loader = loader
    try:
        return loader.execute_entry(ast, interpreter.entry_env, input_info.module_path)
    except OortException as e:
        matched = compiler.error_handler.input_info_for(e.position) or input_info
        compiler.error_handler.add(e, matched)
        compiler.error_handler.report(exit_on_error=False, clear=True, summary=False)
        raise CompilerError() from None


def test_json_example_default_sample(compiled_example, capsys):
    _run_example(compiled_example, None)
    assert capsys.readouterr().out == (
        "{:\n"
        '  "active": true,\n'
        '  "name": "Oort",\n'
        '  "owner": null,\n'
        '  "tags": [\n'
        '    "language",\n'
        '    "interpreter"\n'
        "  ],\n"
        '  "unicode": "你好 😀",\n'
        '  "version": 0.3\n'
        ":}\n"
    )


def test_json_example_runs_on_vm(run_file):
    """The showcase must produce identical output under the bytecode VM."""
    result = run_file(EXAMPLE, target="vm")
    assert result.stdout == (
        "{:\n"
        '  "active": true,\n'
        '  "name": "Oort",\n'
        '  "owner": null,\n'
        '  "tags": [\n'
        '    "language",\n'
        '    "interpreter"\n'
        "  ],\n"
        '  "unicode": "你好 😀",\n'
        '  "version": 0.3\n'
        ":}\n"
    )


def test_json_example_parses_file(compiled_example, capsys):
    _run_example(compiled_example, SAMPLE)
    out = capsys.readouterr().out
    assert '"project": "Oort"' in out
    assert '"frontend": "ANTLR + Pratt"' in out
    assert '"unicode": "你好"' in out


def test_json_example_reports_invalid_json(compiled_example, tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"a": [1, 2,]}', encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        _run_example(compiled_example, bad)
    assert exc_info.value.code == 1
    assert "JSON error: unexpected character ']'" in capsys.readouterr().out


def test_json_example_missing_file_is_a_runtime_error(compiled_example, tmp_path, caplog):
    missing = tmp_path / "missing.json"
    with pytest.raises(CompilerError):
        _run_example(compiled_example, missing)
    assert "No such file or directory" in caplog.text


def _write_text(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "input.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_json_example_escapes_numbers_and_surrogates(compiled_example, tmp_path, capsys):
    path = _write_text(
        tmp_path,
        '{"esc": "a\\"b\\\\c\\n\\t", "num": -1.5e+2, "u": "\\u4F60\\uD83D\\uDE00"}',
    )
    _run_example(compiled_example, path)
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
def test_json_example_rejects_invalid_input(
    compiled_example, tmp_path, capsys, text: str, message: str
):
    path = _write_text(tmp_path, text)
    with pytest.raises(SystemExit) as exc_info:
        _run_example(compiled_example, path)
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "JSON error:" in out
    assert message in out
