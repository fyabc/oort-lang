#! /usr/bin/env python

"""Link typed core modules for the single-module typed VM.

The first P1 slice supports ``from "./lib" import f`` and namespace
``import "./lib"`` function access. Imported modules are lowered independently,
their functions/ADT declarations are merged, and constructor ids are remapped
into the merged module table. Imported constructors are still rejected.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from pathlib import Path

from ..ast import nodes
from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..source.source_position import SourcePosition
from .nodes import (
    BuildAdt,
    DefineFunction,
    HirFunction,
    ImportFrom,
    ImportModule,
    Instruction,
    LoadConst,
    Return,
)
from .typed import AdtDecl, TypedFunction, TypedModule, lower_typed_module

ResolveModule = Callable[[str, Path | None, SourcePosition], tuple[Path, nodes.ModuleNode] | None]


@dataclasses.dataclass
class _TypedUnit:
    path: Path | None
    module: TypedModule


def _merged_decls(units: list[_TypedUnit]) -> tuple[AdtDecl, ...]:
    merged: list[AdtDecl] = []
    seen: set[tuple[str, str]] = set()
    for unit in units:
        for decl in unit.module.adt_decls:
            key = (decl.origin, decl.name)
            if key in seen:
                continue
            seen.add(key)
            merged.append(decl)
    return tuple(merged)


def _constructor_map(unit: _TypedUnit, merged: tuple[AdtDecl, ...]) -> dict[int, int]:
    bases: dict[tuple[str, str], int] = {}
    offset = 0
    for decl in merged:
        bases[(decl.origin, decl.name)] = offset
        offset += len(decl.constructors)
    mapping: dict[int, int] = {}
    local = 0
    for decl in unit.module.adt_decls:
        base = bases[(decl.origin, decl.name)]
        for ctor_index in range(len(decl.constructors)):
            mapping[local] = base + ctor_index
            local += 1
    return mapping


def _remap_hir(
    hir: HirFunction,
    mapping: dict[int, int],
) -> HirFunction:
    code: list[Instruction] = []
    for instruction in hir.code:
        if isinstance(instruction, BuildAdt):
            instruction = dataclasses.replace(
                instruction, constructor_id=mapping[instruction.constructor_id]
            )
        elif isinstance(instruction, DefineFunction):
            # Root functions are kept first, so their indices stay valid.
            instruction = dataclasses.replace(instruction)
        code.append(instruction)
    return dataclasses.replace(hir, code=tuple(code))


def _remap_function(function: TypedFunction, mapping: dict[int, int]) -> TypedFunction:
    return dataclasses.replace(function, hir=_remap_hir(function.hir, mapping))


def _check_imported_main(hir: HirFunction) -> None:
    for instruction in hir.code:
        if isinstance(instruction, (DefineFunction, Return, ImportFrom, ImportModule)):
            continue
        if isinstance(instruction, LoadConst) and instruction.value is None:
            continue
        raise UnsupportedSyntax(
            "Typed imported modules with top-level side effects are not supported yet.",
            hir.position,
        )


def _link(units: list[_TypedUnit]) -> TypedModule:
    merged_decls = _merged_decls(units)
    root = units[-1]
    root_mapping = _constructor_map(root, merged_decls)

    functions: list[TypedFunction] = []
    names: set[str] = set()
    # Keep root functions first: root main's DefineFunction indices are local.
    for unit in [root, *units[:-1]]:
        mapping = root_mapping if unit is root else _constructor_map(unit, merged_decls)
        for function in unit.module.functions:
            if function.hir.name in names:
                raise UnsupportedSyntax(
                    f"Typed imported function name collision: '{function.hir.name}'.",
                    function.hir.position,
                )
            names.add(function.hir.name)
            functions.append(_remap_function(function, mapping))

    for unit in units[:-1]:
        _check_imported_main(unit.module.main.hir)

    main = _remap_function(root.module.main, root_mapping)
    return TypedModule(main, tuple(functions), merged_decls)


def link_typed_modules(
    root_ast: nodes.ModuleNode,
    root_path: Path | None,
    resolve: ResolveModule,
) -> TypedModule:
    """Lower root and its ``from`` imports into one typed module."""

    loaded: dict[Path, _TypedUnit] = {}
    active: set[Path] = set()
    units: list[_TypedUnit] = []

    def binding_name(stmt: nodes.ImportStmt) -> str:
        if stmt.alias:
            return stmt.alias
        name = stmt.module_path.replace("\\", "/").rsplit("/", 1)[-1]
        if name.lower().endswith(".ort"):
            name = name[:-4]
        if not name.isidentifier():
            raise UnsupportedSyntax("Cannot derive a binding name for typed import.", stmt.position)
        return name

    def load(ast: nodes.ModuleNode, path: Path | None) -> _TypedUnit:
        if path is not None and path in loaded:
            return loaded[path]
        if path is not None:
            if path in active:
                raise UnsupportedSyntax("Circular typed import.", ast.position)
            active.add(path)
        module_functions: dict[str, set[str]] = {}
        for stmt in ast.body.statements:
            if isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt)):
                resolved = resolve(stmt.module_path, path, stmt.position)
                if resolved is None:
                    raise UnsupportedSyntax(
                        f"Typed import failed: {stmt.module_path}", stmt.position
                    )
                dep_path, dep_ast = resolved
                dependency = load(dep_ast, dep_path)
                if isinstance(stmt, nodes.ImportStmt):
                    alias = binding_name(stmt)
                    if alias in module_functions:
                        raise UnsupportedSyntax(
                            f"Duplicate typed import binding '{alias}'.", stmt.position
                        )
                    module_functions[alias] = {
                        function.hir.name for function in dependency.module.functions
                    }
        unit = _TypedUnit(path, lower_typed_module(ast, module_functions))
        if path is not None:
            active.discard(path)
            loaded[path] = unit
        units.append(unit)
        return unit

    load(root_ast, root_path)
    return _link(units)


__all__ = ["link_typed_modules"]
