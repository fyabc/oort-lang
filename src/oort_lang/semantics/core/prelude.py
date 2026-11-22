#! /usr/bin/env python

"""The `oort-core` prelude: built-in `Option` and `Result` ADTs.

The declarations are ordinary AST nodes injected at the head of every
`oort-core` module, so the checker, the interpreter and the VM all use the
same generic-enum path.  A fixed nominal origin keeps `Option[Int]` equal
across modules even though each module owns its own injected template.
"""

from ...ast import nodes
from ...ast.nodes.declarations import VarianceKind
from ...source.source_position import SourcePosition

CORE_PRELUDE_ORIGIN = "<core-prelude>"
CORE_PRELUDE_TYPES = frozenset({"Option", "Result"})
CORE_PRELUDE_CONSTRUCTORS = frozenset({"Some", "None", "Ok", "Err"})


def _position() -> SourcePosition:
    return SourcePosition.from_location(1, 0, "<core-prelude>", filename=CORE_PRELUDE_ORIGIN)


def _type_name(name: str) -> nodes.Name:
    return nodes.Name(_position(), name)


def _field(name: str, type_name: str) -> nodes.EnumField:
    return nodes.EnumField(_position(), name, _type_name(type_name))


def _constructor(name: str, fields: list[nodes.EnumField] | None = None) -> nodes.EnumConstructor:
    return nodes.EnumConstructor(_position(), name, fields or ())


def _parameter(name: str) -> nodes.TypeParameter:
    return nodes.TypeParameter(_position(), name, None, variance=VarianceKind.COVARIANT)


def _enum(
    name: str,
    params: list[nodes.TypeParameter],
    constructors: list[nodes.EnumConstructor],
) -> nodes.EnumDef:
    position = _position()
    enum = nodes.EnumDef(
        position,
        name,
        params,
        constructors,
        name_position=position,
        declaration_origin=CORE_PRELUDE_ORIGIN,
    )
    enum.synthetic = True
    return enum


def core_prelude_statements() -> list[nodes.EnumDef]:
    """Build fresh prelude declarations for one module."""
    return [
        _enum(
            "Option",
            [_parameter("T")],
            [
                _constructor("Some", [_field("value", "T")]),
                _constructor("None"),
            ],
        ),
        _enum(
            "Result",
            [_parameter("T"), _parameter("E")],
            [
                _constructor("Ok", [_field("value", "T")]),
                _constructor("Err", [_field("error", "E")]),
            ],
        ),
    ]


def inject_core_prelude(module: nodes.ModuleNode) -> None:
    """Prepend the prelude unless this module already contains it."""
    statements = module.body.statements
    if any(isinstance(stmt, nodes.EnumDef) and stmt.synthetic for stmt in statements):
        return
    statements[0:0] = core_prelude_statements()
