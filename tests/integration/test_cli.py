#! /usr/bin/env python

"""End-to-end command-line tests."""

import sys

import pytest

from oort_lang import __version__
from oort_lang.driver.main import main


def _run_cli(monkeypatch, argv: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", ["oort", *argv])
    with pytest.raises(SystemExit) as exc_info:
        main()
    return exc_info.value.code


def test_cmd_uses_eval_by_default(monkeypatch, capsys):
    assert _run_cli(monkeypatch, ["-c", "print(42)"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "42\n"


def test_file_input(monkeypatch, capsys, tmp_path):
    src = tmp_path / "hello.ort"
    src.write_text('print("hello")\n', encoding="utf-8")
    assert _run_cli(monkeypatch, [str(src)]) == 0
    assert capsys.readouterr().out == "hello\n"


def test_print_ast_target(monkeypatch, capsys):
    assert _run_cli(monkeypatch, ["-t", "ast", "-c", "print(1)"]) == 0
    out = capsys.readouterr().out
    assert "Module" in out
    assert "Call" in out


def test_print_ast_with_metadata(monkeypatch, capsys):
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", "print(1)"]) == 0
    out = capsys.readouterr().out
    assert "Module" in out
    assert "[Metadata]" in out


def test_parse_error_exits_nonzero(monkeypatch, caplog):
    assert _run_cli(monkeypatch, ["-c", "print("]) != 0
    assert "OortSyntaxError" in caplog.text


def test_version(monkeypatch, capsys):
    assert _run_cli(monkeypatch, ["--version"]) == 0
    assert f"Oort {__version__}" in capsys.readouterr().out


def test_relative_import_from_file(monkeypatch, capsys, tmp_path):
    (tmp_path / "lib.ort").write_text("var value = 21\n", encoding="utf-8")
    main = tmp_path / "main.ort"
    main.write_text('import "./lib"\nprint(lib.value * 2)\n', encoding="utf-8")

    assert _run_cli(monkeypatch, [str(main)]) == 0
    assert capsys.readouterr().out == "42\n"


def test_module_path_option(monkeypatch, capsys, tmp_path):
    libs = tmp_path / "libs"
    libs.mkdir()
    (libs / "extra.ort").write_text("var value = 7\n", encoding="utf-8")
    main = tmp_path / "main.ort"
    main.write_text('import "extra"\nprint(extra.value)\n', encoding="utf-8")

    assert _run_cli(monkeypatch, ["-I", str(libs), str(main)]) == 0
    assert capsys.readouterr().out == "7\n"


def test_import_failure_exits_nonzero(monkeypatch, caplog, tmp_path):
    main = tmp_path / "main.ort"
    main.write_text('import "./missing"\n', encoding="utf-8")

    assert _run_cli(monkeypatch, [str(main)]) != 0
    assert "Cannot find module './missing'" in caplog.text


def test_print_ast_shows_import(monkeypatch, capsys, tmp_path):
    main = tmp_path / "main.ort"
    main.write_text('import "./lib" as l\n', encoding="utf-8")

    assert _run_cli(monkeypatch, ["-t", "ast", str(main)]) == 0
    assert "ImportStmt(module_path='./lib', alias='l')" in capsys.readouterr().out


def test_print_ast_with_metadata_accepts_import(monkeypatch, capsys, tmp_path):
    main = tmp_path / "main.ort"
    main.write_text('from "./lib" import value\n', encoding="utf-8")

    assert _run_cli(monkeypatch, ["-t", "astm", str(main)]) == 0
    assert "ImportFromStmt(module_path='./lib', names=[value])" in capsys.readouterr().out
