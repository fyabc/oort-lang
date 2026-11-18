#! /usr/bin/env python

"""REPL integration tests (multi-line input and error recovery)."""

import pytest
from rich.console import Console

from oort_lang.driver.repl import run_repl
from tests.helpers import get_compiler


def _run_repl(monkeypatch, lines: list[str]) -> int:
    iterator = iter(lines)

    def fake_input(self, prompt="", *args, **kwargs):
        try:
            return next(iterator)
        except StopIteration:
            raise KeyboardInterrupt from None

    monkeypatch.setattr(Console, "input", fake_input)
    compiler = get_compiler("NOT_EXIST -t eval")
    return run_repl(compiler)


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


if __name__ == "__main__":
    pytest.main([__file__])
