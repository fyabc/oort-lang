#! /usr/bin/env python

"""Import behavior for trusted native standard-library modules."""

from pathlib import Path

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def _write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


def _run(main: Path):
    return get_compiler(["NOT_EXIST", "-t", "eval"]).run_file(main)


def test_import_and_from_native_module(tmp_path, run_file):
    main = _write(
        tmp_path,
        "main.ort",
        """\
import "math"
from "math" import sqrt
import "string" as text
print(math.floor(math.sqrt(10)))
print(sqrt(9))
print(text.upper("oort"))
""",
    )

    assert run_file(main).stdout == "3\n3.0\nOORT\n"


def test_native_module_is_cached_per_session(tmp_path, run_file):
    main = _write(
        tmp_path,
        "main.ort",
        """\
import "math" as first
import "math" as second
print(first is second)
""",
    )

    assert run_file(main).stdout == "true\n"


def test_native_module_takes_priority_over_bare_file(tmp_path, run_file):
    _write(tmp_path, "math.ort", 'var marker = "local"\n')
    main = _write(
        tmp_path,
        "main.ort",
        """\
import "math"
import "./math" as local_math
print(math.floor(math.sqrt(10)))
print(local_math.marker)
""",
    )

    assert run_file(main).stdout == "3\nlocal\n"


def test_missing_native_export_is_reported(tmp_path, caplog):
    main = _write(tmp_path, "main.ort", 'from "math" import nope\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "does not export 'nope'" in caplog.text


def test_native_module_from_string_input(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    get_compiler(["NOT_EXIST", "-t", "eval"]).run_string(
        'import "math"\nprint(math.floor(math.sqrt(10)))\n'
    )

    assert capsys.readouterr().out == "3\n"
