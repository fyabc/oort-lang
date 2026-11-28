#! /usr/bin/env python

"""Load a typed core module graph for the debug and linking pipelines.

This module owns the source-level graph walk:

- every unit gets a logical module id (relative path, never an absolute path);
- imports are checked against the dependency's export table;
- namespace imports resolve exported functions by alias;
- imported constructors and ADTs are attached for lowering.

Executable linking (relocation, ABI hashes, merged programs) lives in
``bytecode/typed_artifact.py``. ``-t thir`` prints the loaded units with
``format_typed_units``.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from pathlib import Path

from ..ast import nodes
from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..semantics.core.prelude import CORE_PRELUDE_ORIGIN
from ..source.source_position import SourcePosition
from .typed import (
    AdtDecl,
    ConstructorRef,
    TypedModule,
    format_typed_module,
    lower_typed_module,
)

ResolveModule = Callable[[str, Path | None, SourcePosition], tuple[Path, nodes.ModuleNode] | None]

IMPORT_KINDS = ("module", "function", "adt", "constructor")


@dataclasses.dataclass(frozen=True)
class TypedImportRef:
    """One resolved import edge, recorded for the module artifact ABI."""

    module_id: str
    kind: str
    name: str


@dataclasses.dataclass
class TypedUnit:
    path: Path | None
    module_id: str
    ast: nodes.ModuleNode
    module: TypedModule
    functions: set[str]
    constructors: set[str]
    adts: set[str]
    imports: tuple[TypedImportRef, ...] = ()


def _module_id(path: Path | None, root_dir: Path | None) -> str:
    if path is None:
        return "<string>"
    relative = Path(path.name)
    if root_dir is not None:
        try:
            relative = path.relative_to(root_dir)
        except ValueError:
            pass
    text = relative.as_posix()
    if text.lower().endswith(".ort"):
        text = text[:-4]
    return text


def _binding_name(stmt: nodes.ImportStmt) -> str:
    if stmt.alias:
        return stmt.alias
    name = stmt.module_path.replace("\\", "/").rsplit("/", 1)[-1]
    if name.lower().endswith(".ort"):
        name = name[:-4]
    if not name.isidentifier():
        raise UnsupportedSyntax("Cannot derive a binding name for typed import.", stmt.position)
    return name


def _own_decls(module: TypedModule) -> tuple[AdtDecl, ...]:
    return tuple(decl for decl in module.adt_decls if not _is_prelude(decl))


def _is_prelude(decl: AdtDecl) -> bool:
    return decl.origin == CORE_PRELUDE_ORIGIN


def _exports(module: TypedModule) -> tuple[set[str], set[str], set[str]]:
    functions = {function.hir.name for function in module.functions}
    constructors: set[str] = set()
    adts: set[str] = set()
    for decl in _own_decls(module):
        adts.add(decl.name)
        constructors.update(constructor.name for constructor in decl.constructors)
    return functions, constructors, adts


def _find_constructor(module: TypedModule, name: str) -> ConstructorRef | None:
    for decl in _own_decls(module):
        for constructor in decl.constructors:
            if constructor.name == name:
                return ConstructorRef(
                    decl.origin,
                    decl.name,
                    constructor.name,
                    constructor.arity,
                    constructor.payload,
                )
    return None


def load_typed_units(
    root_ast: nodes.ModuleNode,
    root_path: Path | None,
    resolve: ResolveModule,
    *,
    allow_top_level: bool = True,
) -> tuple[TypedUnit, ...]:
    """Load the root module and its typed imports, dependencies first.

    ``allow_top_level=False`` rejects top-level val/var bindings even in the
    entry module; the object→core boundary uses this because exported values
    do not cross the boundary yet (OP 0028).
    """

    boundary_reason = (
        "modules executed across the object→core boundary (module-level values do not cross yet)"
    )

    root_dir = root_path.parent if root_path is not None else None
    loaded: dict[Path, TypedUnit] = {}
    active: set[Path] = set()
    units: list[TypedUnit] = []

    def load(ast: nodes.ModuleNode, path: Path | None, *, is_root: bool) -> TypedUnit:
        if path is not None and path in loaded:
            return loaded[path]
        if path is not None:
            if path in active:
                raise UnsupportedSyntax("Circular typed import.", ast.position)
            active.add(path)

        module_functions: dict[str, set[str]] = {}
        imports: list[TypedImportRef] = []
        external_constructors: dict[str, ConstructorRef] = {}
        external_decls: list[AdtDecl] = []
        seen_decls: set[tuple[str, str]] = set()
        for stmt in ast.body.statements:
            if not isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt)):
                continue
            resolved = resolve(stmt.module_path, path, stmt.position)
            if resolved is None:
                raise UnsupportedSyntax(f"Typed import failed: {stmt.module_path}", stmt.position)
            dep_path, dep_ast = resolved
            dependency = load(dep_ast, dep_path, is_root=False)
            for decl in _own_decls(dependency.module):
                key = (decl.origin, decl.name)
                if key not in seen_decls:
                    seen_decls.add(key)
                    external_decls.append(decl)
            if isinstance(stmt, nodes.ImportStmt):
                alias = _binding_name(stmt)
                if alias in module_functions:
                    raise UnsupportedSyntax(
                        f"Duplicate typed import binding '{alias}'.", stmt.position
                    )
                module_functions[alias] = set(dependency.functions)
                imports.append(TypedImportRef(dependency.module_id, "module", alias))
                continue
            for source_name, local_alias in stmt.names.items():
                if source_name in dependency.functions:
                    imports.append(TypedImportRef(dependency.module_id, "function", source_name))
                    continue
                constructor = _find_constructor(dependency.module, source_name)
                if constructor is not None:
                    local_name = local_alias or source_name
                    external_constructors[local_name] = constructor
                    imports.append(TypedImportRef(dependency.module_id, "constructor", source_name))
                    continue
                if source_name in dependency.adts:
                    raise UnsupportedSyntax(
                        f"'{source_name}' is a type-only export from "
                        f"'{dependency.module_id}'. Use a namespace import.",
                        stmt.position,
                    )
                raise UnsupportedSyntax(
                    f"Module '{dependency.module_id}' does not export '{source_name}'.",
                    stmt.position,
                )

        module = lower_typed_module(
            ast,
            module_functions,
            external_constructors=external_constructors,
            external_decls=tuple(external_decls),
            # A linked program executes only the entry module's main, so
            # top-level bindings can only initialize there.
            allow_top_level=is_root and allow_top_level,
            top_level_reject_reason=(
                boundary_reason
                if not allow_top_level
                else "dependency modules (only the entry module may declare top-level bindings)"
            ),
        )
        functions, constructors, adts = _exports(module)
        unit = TypedUnit(
            path,
            _module_id(path, root_dir),
            ast,
            module,
            functions,
            constructors,
            adts,
            tuple(imports),
        )
        if path is not None:
            active.discard(path)
            loaded[path] = unit
        units.append(unit)
        return unit

    load(root_ast, root_path, is_root=True)
    return tuple(units)


def format_typed_units(units: tuple[TypedUnit, ...]) -> str:
    """Render loaded typed units as a pre-link debug view."""

    blocks: list[str] = []
    for unit in reversed(units):
        body = format_typed_module(unit.module)
        if len(units) > 1:
            body = f"# module {unit.module_id}\n{body}"
        blocks.append(body)
    return "\n\n".join(blocks)


__all__ = [
    "IMPORT_KINDS",
    "ResolveModule",
    "TypedImportRef",
    "TypedUnit",
    "format_typed_units",
    "load_typed_units",
]
