#! /usr/bin/env python

"""End-to-end command-line tests."""

import subprocess
import sys

import pytest

from oort_lang import __version__
from oort_lang.driver.main import main


def _run_cli(monkeypatch, argv: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", ["oort", *argv])
    with pytest.raises(SystemExit) as exc_info:
        main()
    return exc_info.value.code


def test_cmd_uses_vm_by_default(monkeypatch, capsys):
    assert _run_cli(monkeypatch, ["-c", "print(42)"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "42\n"


def test_eval_target_still_available_as_fallback(monkeypatch, capsys):
    assert _run_cli(monkeypatch, ["-t", "eval", "-c", "print(42)"]) == 0
    assert capsys.readouterr().out == "42\n"


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


def test_vm_target_executes_supported_program(monkeypatch, capsys):
    source = """\
def fib(n) {
    if n <= 1: return n
    fib(n - 1) + fib(n - 2)
}
print(fib(10))
"""
    assert _run_cli(monkeypatch, ["-t", "vm", "-c", source]) == 0
    assert capsys.readouterr().out == "55\n"


def test_bytecode_target_prints_disassembly(monkeypatch, capsys):
    source = """\
def f(a) { a + 1 }
print(f(2))
"""
    assert _run_cli(monkeypatch, ["-t", "bc", "-c", source]) == 0
    out = capsys.readouterr().out
    assert "Proto <main>" in out
    assert "Proto f" in out
    assert "DEF_FUN" in out
    assert "CALL" in out


def test_bytecode_target_rejects_unsupported_syntax(monkeypatch, caplog):
    source = "...\n"
    assert _run_cli(monkeypatch, ["-t", "bc", "-c", source]) != 0
    assert "HIR backend does not support ellipsis" in caplog.text


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("'1", "Unterminated string literal"),
        ('"""abc', "Unterminated triple-quoted string literal"),
        ("r'x", "Unterminated string literal"),
        ("\\", "Invalid character '\\\\' (U+005C)"),
        ("`", "Invalid character '`' (U+0060)"),
    ],
)
def test_lexer_error_reports_oort_diagnostic(monkeypatch, caplog, source, message):
    # The source cannot be tokenized. The failure must surface as an Oort
    # diagnostic naming the category and position — not as a raw ANTLR
    # console message — and the process must exit non-zero.
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert f"OortSyntaxError: {message}" in caplog.text
    assert "<string>:1:" in caplog.text


@pytest.mark.parametrize(
    ("source", "message", "position"),
    [
        ("{: '1':", "'{:' was never closed", "<string>:1:1:"),
        ("(1 + 2", "'(' was never closed", "<string>:1:1:"),
        ("[1, 2", "'[' was never closed", "<string>:1:1:"),
        ("if true { print(1)", "'{' was never closed", "<string>:1:9:"),
        ("def f( {}", "'(' was never closed", "<string>:1:6:"),
        ("]", "Unmatched ']'", "<string>:1:1:"),
        ("}", "Unmatched '}'", "<string>:1:1:"),
        (")", "Unmatched ')'", "<string>:1:1:"),
    ],
)
def test_delimiter_error_points_at_the_bracket(monkeypatch, caplog, source, message, position):
    # Broken bracket pairs must point at the bracket itself (Python-style
    # "'X' was never closed" / "Unmatched 'X'"), not wherever the parser
    # happened to give up.
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert f"OortSyntaxError: {message}" in caplog.text
    assert position in caplog.text


@pytest.mark.parametrize(
    ("source", "hint"),
    [
        ("val _ = {1, 2}", "Did you mean a Set literal '{. item, ... .}'?"),
        ("val _ = {1: 2}", "Did you mean a Dict literal '{: key: value :}'?"),
        ("val _ = {1: 2, 3: 4}", "Did you mean a Dict literal '{: key: value :}'?"),
    ],
)
def test_brace_literal_hint(monkeypatch, caplog, source, hint):
    # Python habits (`{1, 2}` / `{1: 2}`) parse as code blocks; the parser
    # error alone is confusing, so a warning suggests Oort's delimiters.
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert "OortSyntaxWarning" in caplog.text
    assert hint in caplog.text


def test_brace_literal_hint_not_fired_for_code_blocks(monkeypatch, caplog):
    # A one-line block wrapping a call (commas nested in parentheses) parses
    # fine and must stay silent; statement keywords are not literal bodies.
    assert _run_cli(monkeypatch, ["-c", "def g(a, b) { a }\nval _ = { g(1, 2) }"]) == 0
    assert _run_cli(monkeypatch, ["-c", "val x = 1\nif true { print(x) }"]) == 0
    assert "OortSyntaxWarning" not in caplog.text


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


def test_core_dialect_runs(monkeypatch, capsys):
    source = "#lang oort-core\ndef f(x: Int) -> Int { x + 1 }\nprint(f(1))\n"
    assert _run_cli(monkeypatch, ["-c", source]) == 0
    assert capsys.readouterr().out == "2\n"


def test_core_type_error_exits_nonzero(monkeypatch, caplog):
    source = "#lang oort-core\nvar x: Bool = 1\n"
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert "TypeCheckError" in caplog.text


def test_core_ast_target_skips_checking(monkeypatch, capsys):
    source = "#lang oort-core\nvar x: Bool = 1\n"
    assert _run_cli(monkeypatch, ["-t", "ast", "-c", source]) == 0
    assert "VarDecl" in capsys.readouterr().out


def test_core_astm_shows_types(monkeypatch, capsys):
    source = "#lang oort-core\nvar x = 1\nprint(x)\n"
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", source]) == 0
    assert "type='Int'" in capsys.readouterr().out


def test_core_astm_shows_class_types(monkeypatch, capsys):
    source = """#lang oort-core
class C {
    val x: Int = 1
}
val c = C()
"""
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", source]) == 0
    out = capsys.readouterr().out
    assert "ClassDef" in out
    assert "type='C'" in out


def test_core_astm_shows_collection_types(monkeypatch, capsys):
    source = """#lang oort-core
val xs = [1, 2]
val pair = (1, true)
"""
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", source]) == 0
    out = capsys.readouterr().out
    assert "type='List[Int]'" in out
    assert "type='Tuple[Int, Bool]'" in out


def test_core_astm_shows_float_and_string_types(monkeypatch, capsys):
    source = """\
#lang oort-core
val x = 1.5
val s = "a" + "b"
"""
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", source]) == 0
    out = capsys.readouterr().out
    assert "type='Float'" in out
    assert "type='String'" in out


def test_core_astm_shows_inferred_function_return_types(monkeypatch, capsys):
    source = """\
#lang oort-core
def add(a: Int, b: Int) { a + b }
def show(n: Int) { print(n) }
val inc = do(x: Int) { x + 1 }
"""
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", source]) == 0
    out = capsys.readouterr().out
    assert "type='(Int, Int) -> Int'" in out
    assert "type='(Int) -> Unit'" in out
    assert "type='(Int) -> Int'" in out


def test_core_module_import_from_file(monkeypatch, capsys, tmp_path):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import add\nprint(add(2, 3))\n',
        encoding="utf-8",
    )
    assert _run_cli(monkeypatch, [str(main)]) == 0
    assert capsys.readouterr().out == "5\n"


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


def test_vm_module_path_option(monkeypatch, capsys, tmp_path):
    libs = tmp_path / "libs"
    libs.mkdir()
    (libs / "extra.ort").write_text(
        "var value = 11\ndef double(x) { x * 2 }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        'import "extra"\nfrom "extra" import double\nprint(extra.value, double(3))\n',
        encoding="utf-8",
    )

    assert _run_cli(monkeypatch, ["-t", "vm", "-I", str(libs), str(main)]) == 0
    assert capsys.readouterr().out == "11 6\n"


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


def _run_repl_subprocess(stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "oort_lang"],
        input=stdin,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )


def test_repl_piped_input_evaluates_and_eof_exits_cleanly():
    proc = _run_repl_subprocess("1 + 2\nprint(4)\n")
    assert proc.returncode == 0
    assert "Out[0]: 3" in proc.stdout
    assert "4\n" in proc.stdout
    assert "Traceback" not in proc.stdout
    assert "Traceback" not in proc.stderr


def test_repl_piped_multiline_input():
    proc = _run_repl_subprocess("var xs = [\n1,\n2,\n]\nprint(xs[1])\n")
    assert proc.returncode == 0
    assert "2\n" in proc.stdout
    assert "Traceback" not in proc.stderr


def test_repl_piped_error_recovers():
    proc = _run_repl_subprocess("1 +\nprint(7)\n")
    assert proc.returncode == 0
    assert "7\n" in proc.stdout
    assert "Traceback" not in proc.stdout
    assert "Traceback" not in proc.stderr


def test_repl_empty_piped_input_exits_zero():
    proc = _run_repl_subprocess("")
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr


def test_repl_incomplete_input_at_eof_reports_syntax_error():
    proc = _run_repl_subprocess("print(\n")
    assert proc.returncode == 0
    # The console wraps the message mid-phrase; the tail survives on one line.
    assert "OortSyntaxError" in proc.stdout
    assert "was never closed" in proc.stdout
    assert "print(" in proc.stdout
    assert "Traceback" not in proc.stdout
    assert "Traceback" not in proc.stderr


def test_print_ast_with_metadata_accepts_import(monkeypatch, capsys, tmp_path):
    main = tmp_path / "main.ort"
    main.write_text('from "./lib" import value\n', encoding="utf-8")

    assert _run_cli(monkeypatch, ["-t", "astm", str(main)]) == 0
    assert "ImportFromStmt(module_path='./lib', names=[value])" in capsys.readouterr().out


def test_core_enum_match_eval(monkeypatch, capsys):
    source = "#lang oort-core\nenum E { A, B(x: Int) }\nprint(match B(3) { A => 0, B(v) => v })\n"
    assert _run_cli(monkeypatch, ["-c", source]) == 0
    assert capsys.readouterr().out == "3\n"


def test_core_enum_match_astm(monkeypatch, capsys):
    source = "#lang oort-core\nenum E { A }\nval x = match A { A => 1 }\n"
    assert _run_cli(monkeypatch, ["-t", "astm", "-c", source]) == 0
    out = capsys.readouterr().out
    assert "EnumDef" in out
    assert "MatchExpr" in out
    assert "type='Int'" in out


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("print(None)", "Name 'None' is not defined (did you mean 'null'?)"),
        ("print(True)", "Name 'True' is not defined (did you mean 'true'?)"),
        ("val x = self", "Name 'self' is not defined (did you mean 'this'?)"),
        # Operators: the VM rejects these at compile time (subset boundary)
        # while the interpreter reports them at runtime, so the prefixes
        # differ; assert the did-you-mean suffix common to both backends.
        ("print(1 && 2)", "(did you mean 'and'?)"),
        ("print(!true)", "(did you mean 'not'?)"),
    ],
)
def test_habit_name_and_operator_suggestions(monkeypatch, caplog, source, message):
    # Python spellings of built-ins and boolean operators get a suffix
    # suggesting the Oort spelling.
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert message in caplog.text


def test_habit_name_suggestion_also_on_vm(monkeypatch, caplog):
    assert _run_cli(monkeypatch, ["-t", "vm", "-c", "print(None)"]) != 0
    assert "did you mean 'null'?" in caplog.text


def test_empty_brace_hint_on_valid_program(monkeypatch, caplog):
    # `val d = {}` parses (an empty block evaluates to null) but is almost
    # certainly a mistyped empty Dict/Set: warn while still exiting zero.
    assert _run_cli(monkeypatch, ["-c", "val d = {}"]) == 0
    assert "Did you mean an empty Dict '{:}' or Set '{.}'?" in caplog.text


@pytest.mark.parametrize(
    ("source", "hint"),
    [
        ("// comment\nprint(1)", "Did you mean a comment? Comments start with '#';"),
        ("var i = 0\ni++", "Oort has no postfix '++'; use += 1."),
        ("val f = lambda(x): x", "'lambda' is not a keyword"),
        ("if x = 1 { }", "did you mean '==' in the condition?"),
    ],
)
def test_habit_hints(monkeypatch, caplog, source, hint):
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert "OortSyntaxWarning" in caplog.text
    assert hint in caplog.text


def test_habit_hints_not_fired_for_valid_code(monkeypatch, caplog):
    source = """\
class D {}
def D.operator "++"(other) { 2 }
def f() {}
val xs = {. 1 .}
val d = {: "a": 1 :}
print(f(), xs, d)
"""
    assert _run_cli(monkeypatch, ["-c", source]) == 0
    assert "OortSyntaxWarning" not in caplog.text


def test_plain_output_keeps_messages_on_one_line():
    proc = subprocess.run(
        [sys.executable, "-m", "oort_lang", "--plain", "-c", "if true { print(1)"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert proc.returncode != 0
    # Plain output is one line per record; the message must stay contiguous.
    assert "'{' was never closed" in proc.stdout + proc.stderr
    assert "Traceback" not in proc.stderr


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("{.5}", "Unmatched '}': expected '.}' to close '{.'"),
        ("{: 'a': 1}", "Unmatched '}': expected ':}' to close '{:'"),
        ("(]", "Unmatched ']': expected ')' to close '('"),
    ],
)
def test_mismatched_delimiter_pairs(monkeypatch, caplog, source, message):
    # When a closer does not match the pending opener, name the closer the
    # opener expects (Python 3.12 pairs closing/opening objects the same way).
    assert _run_cli(monkeypatch, ["-c", source]) != 0
    assert message in caplog.text


def test_leading_dot_float_is_rejected(monkeypatch, caplog):
    # PointFloat requires a digit before the point (OP 0021): `.5` is a
    # parse error with a did-you-mean hint; `0.5`/`1.5e3` stay valid.
    assert _run_cli(monkeypatch, ["-c", "val x = .5"]) != 0
    assert "Leading-dot floats are not supported; did you mean '0.5'?" in caplog.text


def test_float_literals_with_integer_part_stay_valid(monkeypatch, caplog):
    assert (
        _run_cli(monkeypatch, ["-c", "val a = 0.5\nval b = 1.5e3\nval c = 2e3\nprint(a, b, c)"])
        == 0
    )
    assert "OortSyntaxWarning" not in caplog.text
