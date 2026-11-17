#! /usr/bin/env python

"""Tests for the `#lang` directive and dialect configuration."""

import pytest

from oort_lang.frontend.dialect import (
    DEFAULT_DIALECT,
    OORT_CORE,
    OORT_OBJECT,
    known_dialect_names,
    lookup_dialect,
    parse_lang_directive,
)
from oort_lang.frontend.operator_defs import Arity
from tests.helpers import get_compiler


class TestDialectRegistry:
    def test_default_is_oort_object(self):
        assert DEFAULT_DIALECT is OORT_OBJECT
        assert lookup_dialect("oort-object") is OORT_OBJECT

    def test_unimplemented_dialect_is_registered(self):
        assert lookup_dialect("oort-core") is OORT_CORE
        assert OORT_CORE.implemented is False
        assert known_dialect_names() == ["oort-object", "oort-core"]

    def test_unknown_dialect(self):
        assert lookup_dialect("oort-nope") is None

    def test_each_config_gets_a_fresh_operator_table(self):
        first = OORT_OBJECT.new_operator_table()
        second = OORT_OBJECT.new_operator_table()
        assert first is not second
        assert first.get("+", Arity.INFIX) is not None
        assert second.get("+", Arity.INFIX) is not None


class TestParseLangDirective:
    def test_no_directive(self):
        directive = parse_lang_directive("print(1)\n")
        assert directive.dialect_name is None
        assert directive.error is None
        assert directive.has_directive is False

    def test_explicit_directive(self):
        directive = parse_lang_directive("#lang oort-object\nprint(1)\n")
        assert directive.dialect_name == "oort-object"
        assert directive.error is None
        assert (directive.line, directive.column) == (1, 0)
        assert directive.text == "#lang oort-object"

    def test_directive_with_crlf_and_bom(self):
        directive = parse_lang_directive("﻿#lang oort-object\r\nprint(1)\r\n")
        assert directive.dialect_name == "oort-object"
        assert directive.error is None

    def test_empty_source(self):
        directive = parse_lang_directive("")
        assert directive.dialect_name is None
        assert directive.error is None

    @pytest.mark.parametrize(
        "source",
        [
            "#lang\n",
            "#lang \n",
            "#lang oort-object extra\n",
            "#lang oort object\n",
        ],
    )
    def test_invalid_directive(self, source: str):
        directive = parse_lang_directive(source)
        assert directive.error is not None
        assert "Invalid `#lang` directive" in directive.error
        assert (directive.line, directive.column) == (1, 0)

    def test_lookalike_comment_is_not_a_directive(self):
        directive = parse_lang_directive("#language oort-object\nprint(1)\n")
        assert directive.dialect_name is None
        assert directive.error is None

    def test_misplaced_directive(self):
        directive = parse_lang_directive("print(1)\n#lang oort-object\n")
        assert directive.error is not None
        assert "must be the first line" in directive.error
        assert (directive.line, directive.column) == (2, 0)


class TestDialectRouting:
    def test_explicit_default_dialect_runs(self, run_source):
        result = run_source("#lang oort-object\nprint(1)\n")
        assert result.stdout == "1\n"

    def test_unknown_dialect_is_reported(self, caplog: pytest.LogCaptureFixture):
        compiler = get_compiler("NOT_EXIST -t eval")
        with pytest.raises(SystemExit):
            compiler.run_string("#lang oort-nope\n")
        assert "Unknown dialect 'oort-nope'" in caplog.text
        assert "Known dialects: oort-object, oort-core" in caplog.text
        assert "<string>:1:1" in caplog.text

    def test_unimplemented_dialect_is_reported(self, caplog: pytest.LogCaptureFixture):
        compiler = get_compiler("NOT_EXIST -t eval")
        with pytest.raises(SystemExit):
            compiler.run_string("#lang oort-core\n")
        assert "The 'oort-core' dialect is not implemented yet." in caplog.text

    def test_misplaced_directive_is_reported(self, caplog: pytest.LogCaptureFixture):
        compiler = get_compiler("NOT_EXIST -t eval")
        with pytest.raises(SystemExit):
            compiler.run_string("print(1)\n#lang oort-object\n")
        assert "must be the first line" in caplog.text
        assert "<string>:2:1" in caplog.text

    def test_directive_does_not_change_line_numbers(self, caplog: pytest.LogCaptureFixture):
        compiler = get_compiler("NOT_EXIST -t eval")
        with pytest.raises(SystemExit):
            compiler.run_string("#lang oort-object\nvar a = 1\n{ var a = a }\n")
        assert "<string>:3:" in caplog.text
        assert "Can't read local variable a in its own initializer." in caplog.text
