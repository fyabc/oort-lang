#! /usr/bin/env python

"""Tests for standard diagnostic rendering (GCC/Clang style)."""

from oort_lang.diagnostics.render import render_diagnostic, render_note, resolve_color
from oort_lang.source.input_info import StringInputInfo
from oort_lang.source.source_position import SourcePosition


class _Stream:
    def __init__(self, tty: bool):
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


def _position(column: int = 8) -> SourcePosition:
    return SourcePosition.from_location(1, column, "a", filename="a.ort")


def test_header_and_caret_follow_standard_layout():
    input_info = StringInputInfo("var a = a\n", name="a.ort")
    text = render_diagnostic(
        "Can't read local variable in its own initializer.",
        _position(),
        input_info,
        severity="error",
        kind="OortNameError",
    )
    lines = text.splitlines()
    assert lines[0] == (
        "a.ort:1:9: error[OortNameError]: Can't read local variable in its own initializer."
    )
    assert lines[1] == "var a = a"
    assert lines[2] == "        ^"
    assert "\x1b[" not in text


def test_color_is_opt_in():
    input_info = StringInputInfo("var a = a\n", name="a.ort")
    colored = render_diagnostic("boom", _position(), input_info, kind="OortSyntaxError", color=True)
    assert "\x1b[1;31m" in colored  # red severity label
    assert "\x1b[1;36m" in colored  # cyan caret
    assert colored.endswith("\x1b[0m") or "\x1b[0m" in colored

    note = render_note("called from module", _position(), input_info, color=True)
    assert "\x1b[1;36m" in note
    assert "called from module" in note
    assert "a.ort:1:9" in note


def test_warning_uses_warning_severity():
    input_info = StringInputInfo("val x = 1\n", name="a.ort")
    text = render_diagnostic(
        "careful",
        SourcePosition.from_location(1, 0, "val", filename="a.ort"),
        input_info,
        severity="warning",
        kind="OortSyntaxWarning",
    )
    assert text.startswith("a.ort:1:1: warning[OortSyntaxWarning]: careful")


def test_resolve_color_precedence(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)

    assert resolve_color("auto", _Stream(True))
    assert not resolve_color("auto", _Stream(False))

    monkeypatch.setenv("NO_COLOR", "1")
    assert not resolve_color("auto", _Stream(True))
    monkeypatch.delenv("NO_COLOR")

    monkeypatch.setenv("FORCE_COLOR", "1")
    assert resolve_color("auto", _Stream(False))
    assert resolve_color("always", _Stream(False))
    assert not resolve_color("never", _Stream(True))
