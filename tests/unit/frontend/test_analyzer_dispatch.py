#! /usr/bin/env python

"""Tests for dialect-driven semantic analyzer selection."""

from oort_lang.parser.dialect import OORT_CORE, OORT_OBJECT
from oort_lang.semantics.analyzer import CoreAnalyzer, create_semantic_analyzer
from oort_lang.semantics.pass1 import Pass1Analyzer
from oort_lang.source.input_info import StringInputInfo
from tests.helpers import get_compiler


def _analyzer(dialect):
    compiler = get_compiler("NOT_EXIST -t eval")
    input_info = StringInputInfo("")
    return create_semantic_analyzer(compiler.error_handler, input_info, dialect)


def test_object_uses_pass1_analyzer():
    assert isinstance(_analyzer(OORT_OBJECT), Pass1Analyzer)


def test_core_uses_core_analyzer():
    analyzer = _analyzer(OORT_CORE)
    assert isinstance(analyzer, CoreAnalyzer)
    assert isinstance(analyzer.pass1, Pass1Analyzer)


def test_compiler_factory_uses_dialect():
    compiler = get_compiler("NOT_EXIST -t eval")
    input_info = StringInputInfo("")
    assert isinstance(compiler.make_semantic_analyzer(input_info, OORT_OBJECT), Pass1Analyzer)
    assert isinstance(compiler.make_semantic_analyzer(input_info, OORT_CORE), CoreAnalyzer)
