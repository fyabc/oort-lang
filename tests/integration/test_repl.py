#! /usr/bin/env python

"""REPL integration tests (multi-line input and error recovery)."""

import pytest
from rich.console import Console

from oort_lang import __version__
from oort_lang.driver.repl import ReplAction, ReplSession, run_repl
from tests.helpers import get_compiler


def _run_repl(monkeypatch, lines: list[str]) -> int:
    iterator = iter(lines)

    def fake_input(self, prompt="", *args, **kwargs):
        try:
            return next(iterator)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr(Console, "input", fake_input)
    compiler = get_compiler("NOT_EXIST -t eval")
    return run_repl(compiler)


def _run_repl_events(monkeypatch, events: list[object]):
    pending = list(events)

    def fake_input(self, prompt="", *args, **kwargs):
        event = pending.pop(0)
        if isinstance(event, BaseException):
            raise event
        return event

    monkeypatch.setattr(Console, "input", fake_input)
    return run_repl(get_compiler("NOT_EXIST -t eval"))


def test_repl_ctrl_c_at_prompt_cancels_without_exiting(monkeypatch, capsys):
    code = _run_repl_events(monkeypatch, [KeyboardInterrupt(), "1 + 2", EOFError()])
    assert code == 0
    out = capsys.readouterr().out
    assert "Input cancelled." in out
    assert "Out[0]: 3" in out


def test_repl_ctrl_c_discards_pending_multiline_input(monkeypatch, capsys):
    code = _run_repl_events(
        monkeypatch, ["var xs = [", KeyboardInterrupt(), "print(1)", EOFError()]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "Input cancelled." in out
    assert "1\n" in out


@pytest.mark.parametrize("command", ["exit", "quit", "  exit  "])
def test_repl_exit_commands(monkeypatch, capsys, command: str):
    assert _run_repl(monkeypatch, [command, "print(1)"]) == 0
    assert "Out[" not in capsys.readouterr().out


def test_repl_ctrl_c_during_evaluation_returns_to_prompt(monkeypatch, capsys):
    original = ReplSession.feed_line
    state = {"calls": 0}

    def fake_feed(self, line):
        if state["calls"] == 0:
            state["calls"] += 1
            raise KeyboardInterrupt
        return original(self, line)

    monkeypatch.setattr(ReplSession, "feed_line", fake_feed)
    assert _run_repl(monkeypatch, ["1 + 2", "print(5)"]) == 0
    out = capsys.readouterr().out
    assert "Interrupted." in out
    assert "5\n" in out


def test_repl_banner_uses_package_version(monkeypatch, capsys):
    assert _run_repl(monkeypatch, []) == 0
    assert f"Oort {__version__}" in capsys.readouterr().out


def test_repl_rejects_lang_directive(monkeypatch, capsys, caplog):
    assert _run_repl(monkeypatch, ["#lang oort-core", "print(7)"]) == 0
    assert "Dialect directives are not supported in the REPL" in caplog.text
    assert "7\n" in capsys.readouterr().out


def test_repl_annotations_remain_dynamic(monkeypatch, capsys):
    assert _run_repl(monkeypatch, ["var x: Bool = 1", "print(x + 1)"]) == 0
    assert "2\n" in capsys.readouterr().out


def test_repl_evaluates_expression(monkeypatch, capsys):
    assert _run_repl(monkeypatch, ["1 + 2"]) == 0
    assert "3" in capsys.readouterr().out


def test_repl_multiline_input(monkeypatch, capsys):
    lines = ["var xs = [", "1, 2,", "]", "print(xs[1])"]
    assert _run_repl(monkeypatch, lines) == 0
    assert "2" in capsys.readouterr().out


def test_repl_recovers_from_error(monkeypatch, capsys, caplog):
    lines = ["1 +", "print(7)"]
    assert _run_repl(monkeypatch, lines) == 0
    assert "7" in capsys.readouterr().out
    assert "OortSyntaxError" in caplog.text


def test_repl_continuation_with_backslash(monkeypatch, capsys):
    assert _run_repl(monkeypatch, ["1 + \\", "2"]) == 0
    assert "3" in capsys.readouterr().out


def test_repl_import_relative_to_cwd(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "lib.ort").write_text("var value = 3\n", encoding="utf-8")

    lines = ['import "./lib"', "print(lib.value)"]
    assert _run_repl(monkeypatch, lines) == 0
    assert "3" in capsys.readouterr().out


def test_repl_from_import_persists(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "lib.ort").write_text("var value = 4\n", encoding="utf-8")

    lines = ['from "./lib" import value', "print(value)"]
    assert _run_repl(monkeypatch, lines) == 0
    assert "4" in capsys.readouterr().out


def test_repl_recovers_from_import_error(monkeypatch, capsys, caplog, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "lib.ort").write_text("var value = 5\n", encoding="utf-8")

    lines = ['import "./missing"', 'import "./lib"', "print(lib.value)"]
    assert _run_repl(monkeypatch, lines) == 0
    assert "Cannot find module './missing'" in caplog.text
    assert "5" in capsys.readouterr().out


def test_repl_native_modules(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    lines = [
        'import "math"',
        'from "string" import upper',
        "print(math.floor(math.sqrt(10)))",
        'print(upper("oort"))',
    ]
    assert _run_repl(monkeypatch, lines) == 0
    out = capsys.readouterr().out
    assert "3" in out
    assert "OORT" in out


def _session() -> ReplSession:
    return ReplSession(get_compiler("NOT_EXIST -t eval"))


def test_session_reports_continuation_then_evaluates():
    session = _session()
    assert session.feed_line("var xs = [").action is ReplAction.CONTINUE
    assert session.is_continuing
    assert session.feed_line("1, 2,").action is ReplAction.CONTINUE
    result = session.feed_line("]")
    assert result.action is ReplAction.EVALUATED
    assert result.value is None  # declarations produce null
    assert session.statement_count == 1
    assert not session.is_continuing

    result = session.feed_line("xs[1]")
    assert result.action is ReplAction.EVALUATED
    assert result.index == 1
    assert result.value is not None


def test_session_keeps_environment_after_error():
    session = _session()
    session.feed_line("var value = 3")
    result = session.feed_line("1 +")
    assert result.action is ReplAction.ERROR
    assert not session.is_continuing

    result = session.feed_line("print(value)")
    assert result.action is ReplAction.EVALUATED


def test_session_cancel_discards_pending_input():
    session = _session()
    session.feed_line("[1,")
    assert session.is_continuing
    session.cancel()
    assert not session.is_continuing
    assert session.feed_line("2 + 2").action is ReplAction.EVALUATED


def test_session_trailing_backslash_continues():
    session = _session()
    assert session.feed_line("1 + \\").action is ReplAction.CONTINUE
    assert session.feed_line("2").action is ReplAction.EVALUATED


def test_session_ignores_empty_input_when_idle():
    session = _session()
    assert session.feed_line("   ").action is ReplAction.EMPTY
    assert session.statement_count == 0


if __name__ == "__main__":
    pytest.main([__file__])
