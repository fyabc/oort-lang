#! /usr/bin/env python

"""Typed name bindings and scope layouts."""

import pytest

from oort_lang.ast import nodes
from oort_lang.ast.binding import Binding
from oort_lang.frontend.scope import ScopeLayout
from tests.helpers import build_ast


def _walk(node: nodes.ASTNode):
    yield node
    for child in node.children():
        yield from _walk(child)


def _names(ast: nodes.ASTNode, name: str) -> list[nodes.Name]:
    return [node for node in _walk(ast) if isinstance(node, nodes.Name) and node.id == name]


def test_binding_invariants():
    with pytest.raises(ValueError):
        Binding("x", depth=None, index=0)
    with pytest.raises(ValueError):
        Binding("x", depth=0)
    with pytest.raises(ValueError):
        Binding("x", depth=-1, index=0)
    with pytest.raises(ValueError):
        Binding("x", depth=0, index=-1)


def test_scope_layout_assigns_slots_in_declaration_order():
    scope = ScopeLayout()
    scope.put("a")
    scope.put("b")
    scope.set_ready("a")

    assert scope["a"].index == 0
    assert scope["b"].index == 1
    assert scope["a"].is_ready is True
    assert scope["b"].is_ready is False
    assert scope.resolve("missing", depth=0) is None

    binding = scope.resolve("b", depth=2)
    assert binding == Binding.local("b", depth=2, index=1)


def test_every_name_is_resolved():
    ast = build_ast(
        """\
var g = 1
{
    var a = 2
    {
        print(a, g)
    }
}
"""
    )

    for node in _walk(ast):
        if isinstance(node, (nodes.Name, nodes.ImplicitSuperExpr)):
            assert node.binding is not None
            if isinstance(node, nodes.Name):
                assert node.binding.name == node.id


def test_nested_scope_depths_and_slots():
    ast = build_ast(
        """\
var g = 1
{
    var a = 2
    var b = 3
    {
        print(a, b, g)
    }
}
"""
    )

    (a,) = _names(ast, "a")
    (b,) = _names(ast, "b")
    (g,) = _names(ast, "g")
    (print_name,) = _names(ast, "print")

    assert a.binding == Binding.local("a", depth=1, index=0)
    assert b.binding == Binding.local("b", depth=1, index=1)
    assert g.binding == Binding.global_binding("g")
    assert print_name.binding == Binding.global_binding("print")


def test_binding_depth_tracks_nesting():
    depth = 6
    lines = ["{"]
    for level in range(depth):
        lines.append(f"var v{level} = {level}")
        if level < depth - 1:
            lines.append("{")
    used = ", ".join(f"v{level}" for level in range(depth))
    lines.append(f"print({used})")
    for _ in range(depth):
        lines.append("}")

    ast = build_ast("\n".join(lines) + "\n")
    for level in range(depth):
        (name_node,) = _names(ast, f"v{level}")
        assert name_node.binding == Binding.local(f"v{level}", depth=depth - 1 - level, index=0)


def test_implicit_super_is_bound_to_this():
    ast = build_ast(
        """\
class A {
    def f() { 1 }
}
class B < A {
    def f() { super.f() }
}
"""
    )

    implicit_super = [node for node in _walk(ast) if isinstance(node, nodes.ImplicitSuperExpr)]
    assert len(implicit_super) == 1
    assert implicit_super[0].binding is not None
    assert implicit_super[0].binding.name == "this"
    assert not implicit_super[0].binding.is_global
