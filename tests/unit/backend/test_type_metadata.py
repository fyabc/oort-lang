#! /usr/bin/env python

"""Checker records structured expression types for typed HIR lowering (design 15, T1)."""

from oort_lang.ast.nodes.base import ASTNode
from oort_lang.ast.nodes.expressions import Expression
from oort_lang.semantics.core.types import Type
from tests.helpers import build_ast

SOURCE = """\
#lang oort-core

def fact(n: Int) -> Int {
    if n <= 1 { 1 } else { n * fact(n - 1) }
}

def main2() -> Unit {
    var total: Int = 0
    var i: Int = 0
    while i < 5 {
        total = total + i
        i = i + 1
    }
    print(fact(total))
}

main2()
"""


def _walk(node: ASTNode):
    yield node
    for child in node.children():
        yield from _walk(child)


def test_every_expression_has_structured_type():
    ast = build_ast(SOURCE)
    expressions = [node for node in _walk(ast) if isinstance(node, Expression)]

    assert expressions
    missing = [type(node).__name__ for node in expressions if "type_obj" not in node.metadata]
    assert missing == []


def test_recorded_types_are_structured_type_objects():
    ast = build_ast(SOURCE)

    for node in _walk(ast):
        if isinstance(node, Expression):
            assert isinstance(node.metadata["type_obj"], Type), type(node).__name__
