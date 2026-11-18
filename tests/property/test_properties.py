#! /usr/bin/env python

"""Property-based checks (run with `--with hypothesis` in CI)."""

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, settings
from hypothesis import strategies as st

from oort_lang.ast import nodes
from oort_lang.ast.binding import Binding
from tests.helpers import build_ast, get_compiler

_INTEGER = st.integers(min_value=-(10**6), max_value=10**6).map(str)


def _combine(children):
    return st.one_of(
        st.builds(lambda a, b: f"({a} + {b})", children, children),
        st.builds(lambda a, b: f"({a} - {b})", children, children),
        st.builds(lambda a, b: f"({a} * {b})", children, children),
    )


_EXPRESSION = st.recursive(_INTEGER, _combine, max_leaves=10)


@settings(max_examples=100, deadline=None)
@given(expression=_EXPRESSION)
def test_integer_arithmetic_matches_python(expression: str):
    compiler = get_compiler("NOT_EXIST -t eval")
    assert compiler.run_string(expression) == eval(expression)


def _walk(node):
    yield node
    for child in node.children():
        yield from _walk(child)


@settings(max_examples=50, deadline=None)
@given(depth=st.integers(min_value=1, max_value=8))
def test_binding_depths_follow_nesting(depth: int):
    lines = ["{"]
    for level in range(depth):
        lines.append(f"var v{level} = {level}")
        if level < depth - 1:
            lines.append("{")
    lines.append("print(" + ", ".join(f"v{level}" for level in range(depth)) + ")")
    lines.extend("}" for _ in range(depth))

    ast = build_ast("\n".join(lines) + "\n")
    for node in _walk(ast):
        if isinstance(node, nodes.Name) and node.id.startswith("v"):
            level = int(node.id[1:])
            assert node.binding == Binding.local(node.id, depth - 1 - level, index=0)
