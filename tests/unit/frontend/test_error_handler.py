#! /usr/bin/env python

"""Tests for multi-input diagnostic pairing and ordering."""

import logging

import pytest

from oort_lang.diagnostics import OortSyntaxError, OortSyntaxWarning
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.source.input_info import StringInputInfo
from oort_lang.source.source_position import SourcePosition


def _position(filename: str, line: int = 1) -> SourcePosition:
    return SourcePosition.from_location(line, 0, "stmt", filename=filename)


def test_errors_are_sorted_across_files_with_their_own_source(
    caplog: pytest.LogCaptureFixture,
):
    handler = CompilerErrorHandler()
    first = StringInputInfo("print(1)\n", name="b.ort")
    second = StringInputInfo("print(2)\n", name="a.ort")
    handler.register_input(first)
    handler.register_input(second)

    handler.add(OortSyntaxError("error-b", _position("b.ort")), first)
    handler.add(OortSyntaxError("error-a", _position("a.ort")), second)

    caplog.set_level(logging.INFO)
    assert handler.report(clear=False, summary=False) == 2

    output = caplog.text
    assert output.index("error-a") < output.index("error-b")
    assert "print(1)" in output
    assert "print(2)" in output


def test_add_resolves_input_info_from_position():
    handler = CompilerErrorHandler()
    input_info = StringInputInfo("print(1)\n", name="a.ort")
    handler.register_input(input_info)

    handler.add(OortSyntaxError("boom", _position("a.ort")))

    assert handler.input_info_for(_position("a.ort")) is input_info
    assert handler.error_count == 1


def test_traceback_positions_use_their_own_source(caplog: pytest.LogCaptureFixture):
    handler = CompilerErrorHandler()
    module_input = StringInputInfo('import "./dep"\n', name="main.ort")
    handler.register_input(module_input)

    error = OortSyntaxError("boom", _position("main.ort"))
    error.add_traceback("called from module", _position("dep.ort"))
    handler.add(error, module_input)

    caplog.set_level(logging.INFO)
    handler.report(clear=False, summary=False)

    assert "dep.ort:1:1" in caplog.text
    assert "called from module" in caplog.text


def test_warnings_do_not_count_as_errors():
    handler = CompilerErrorHandler()
    input_info = StringInputInfo("print(1)\n", name="a.ort")
    handler.register_input(input_info)
    handler.add(OortSyntaxWarning("careful", _position("a.ort")), input_info)

    assert handler.error_count == 0
    assert handler.pending_count == 1
    assert handler.report(clear=False, summary=False) == 0
