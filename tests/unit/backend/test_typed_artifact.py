#! /usr/bin/env python

"""Typed module artifacts (v8) and the link-time loader (design 19)."""

import dataclasses

import pytest

from oort_lang.ast import nodes
from oort_lang.bytecode import (
    TypedCodeVM,
    build_typed_artifact,
    build_typed_program,
    compile_typed_module,
    link_typed_artifacts,
    read_linked_bundle,
    read_typed_artifact,
    read_typed_obc,
    write_linked_bundle,
    write_typed_artifact,
    write_typed_obc,
)
from oort_lang.bytecode.serialize import ObcError
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.diagnostics.syntax_errors import UnsupportedSyntax
from oort_lang.hir import lower_typed_module
from oort_lang.hir.typed_link import TypedImportRef, TypedUnit
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.semantics.core.prelude import inject_core_prelude
from oort_lang.source.input_info import StringInputInfo
from tests.helpers import get_compiler


def _check(source: str, name: str):
    """Parse and semantically check one core module with a distinct origin."""

    compiler = get_compiler("NOT_EXIST -t eval")
    info = StringInputInfo(source, name=name)
    compiler.error_handler.register_input(info)
    dialect = compiler._resolve_dialect(info)
    assert dialect is not None
    parser, tokenized = compiler.prepare_parser(info)
    ast = compiler.build_ast(parser, info, dialect=dialect, tokenized=tokenized)
    assert isinstance(ast, nodes.ModuleNode)
    inject_core_prelude(ast)
    analyzer = compiler.make_semantic_analyzer(info, dialect)
    checked = compiler.semantic_analyze(ast, analyzer)
    assert isinstance(checked, nodes.ModuleNode)
    return checked


def _unit(source: str, module_id: str, imports=()) -> TypedUnit:
    ast = _check(source, f"{module_id}.ort")
    module = lower_typed_module(ast)
    functions = {function.hir.name for function in module.functions}
    adts = {decl.name for decl in module.adt_decls}
    constructors = {
        constructor.name for decl in module.adt_decls for constructor in decl.constructors
    }
    return TypedUnit(
        None,
        module_id,
        ast,
        module,
        functions,
        constructors,
        adts,
        tuple(imports),
    )


def test_artifact_round_trip_is_path_free(tmp_path):
    unit = _unit(
        """#lang oort-core
enum Color { Red, Green }
def paint(color: Color) -> Int { match color { Red => 1, Green => 2 } }
print(paint(Red))
""",
        "solo",
    )
    artifact = build_typed_artifact(unit)
    path = tmp_path / "solo.obc"
    write_typed_artifact(artifact, path)

    loaded = read_typed_artifact(path)

    assert loaded.module_id == "solo"
    assert loaded.abi_version == artifact.abi_version
    export_keys = {(export.kind, export.name) for export in loaded.exports}
    assert export_keys >= {
        ("function", "paint"),
        ("adt", "Color"),
        ("constructor", "Red"),
        ("constructor", "Green"),
    }
    assert ("adt", "Option") not in export_keys
    assert ("constructor", "Some") not in export_keys
    assert {ref.name for ref in loaded.constructors if ref.origin == "solo"} >= {
        "Red",
        "Green",
    }
    raw = path.read_bytes()
    assert str(tmp_path).encode() not in raw
    assert b"solo" in raw
    for decl in loaded.program.adt_decls:
        assert decl.origin in {"solo", "<core-prelude>"}


def test_v8_and_v6_artifacts_do_not_cross_read(tmp_path):
    unit = _unit("#lang oort-core\nprint(1)\n", "solo")
    artifact = build_typed_artifact(unit)
    v8_path = tmp_path / "v8.obc"
    write_typed_artifact(artifact, v8_path)

    dynamic_source = "#lang oort-core\ndef one() -> Int { 1 }\nprint(one())\n"
    v6_path = tmp_path / "v6.obc"
    write_typed_obc(
        compile_typed_module(lower_typed_module(_check(dynamic_source, "v6.ort"))),
        v6_path,
    )

    with pytest.raises(ObcError, match="unsupported typed module artifact version 6"):
        read_typed_artifact(v6_path)
    with pytest.raises(ObcError, match="unsupported typed bytecode version 8"):
        read_typed_obc(v8_path)


def test_link_artifacts_remaps_same_named_adts(tmp_path, capsys):
    lib = _unit(
        """#lang oort-core
enum Color { Blue, Red }
def add(a: Int, b: Int) -> Int { a + b }
""",
        "lib",
    )
    main = _unit(
        """#lang oort-core
enum Color { Red }
print(Red)
""",
        "main",
        imports=(TypedImportRef("lib", "module", "lib"),),
    )

    lib_artifact = build_typed_artifact(lib)
    main_artifact = build_typed_artifact(main)
    lib_path = tmp_path / "lib.obc"
    main_path = tmp_path / "main.obc"
    write_typed_artifact(lib_artifact, lib_path)
    write_typed_artifact(main_artifact, main_path)

    linked = link_typed_artifacts(
        read_typed_artifact(main_path),
        {
            "lib": read_typed_artifact(lib_path),
            "main": read_typed_artifact(main_path),
        },
    )

    origins = {decl.origin for decl in linked.adt_decls}
    assert {"lib", "main"} <= origins
    names = {function.name for function in linked.functions}
    assert "add" in names

    TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(linked)
    assert capsys.readouterr().out == "Red\n"


def test_link_artifacts_rejects_missing_export(tmp_path):
    lib = _unit("#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n", "lib")
    main = _unit(
        "#lang oort-core\nprint(1)\n",
        "main",
        imports=(TypedImportRef("lib", "function", "missing"),),
    )
    lib_artifact = build_typed_artifact(lib)
    main_artifact = build_typed_artifact(main)

    with pytest.raises(UnsupportedSyntax, match="does not export function 'missing'"):
        link_typed_artifacts(main_artifact, {"lib": lib_artifact, "main": main_artifact})


def test_exports_carry_abi_hashes(tmp_path):
    unit = _unit(
        """#lang oort-core
enum Color { Red, Green }
def add(a: Int, b: Int) -> Int { a + b }
""",
        "solo",
    )
    artifact = build_typed_artifact(unit)

    hashes = {(export.kind, export.name): export.abi_hash for export in artifact.exports}
    assert hashes[("function", "add")] != 0
    assert hashes[("adt", "Color")] != 0
    assert hashes[("constructor", "Red")] != 0
    assert hashes[("constructor", "Red")] != hashes[("constructor", "Green")]


def test_link_artifacts_rejects_abi_hash_mismatch():
    lib = build_typed_artifact(
        _unit("#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n", "lib")
    )
    main = build_typed_artifact(
        _unit(
            "#lang oort-core\nprint(1)\n",
            "main",
            imports=(TypedImportRef("lib", "function", "add"),),
        )
    )
    tampered = dataclasses.replace(
        main,
        imports=(dataclasses.replace(main.imports[0], expected_abi_hash=1),),
    )

    with pytest.raises(UnsupportedSyntax, match="Typed ABI hash mismatch"):
        link_typed_artifacts(tampered, {"lib": lib, "main": tampered})


def test_link_artifacts_rejects_missing_module():
    main = _unit(
        "#lang oort-core\nprint(1)\n",
        "main",
        imports=(TypedImportRef("nope", "module", "nope"),),
    )
    artifact = build_typed_artifact(main)

    with pytest.raises(UnsupportedSyntax, match="imports missing module 'nope'"):
        link_typed_artifacts(artifact, {"main": artifact})


def test_link_artifacts_rejects_cycle():
    a = build_typed_artifact(
        _unit(
            "#lang oort-core\nprint(1)\n",
            "a",
            imports=(TypedImportRef("b", "module", "b"),),
        )
    )
    b = build_typed_artifact(
        _unit(
            "#lang oort-core\nprint(2)\n",
            "b",
            imports=(TypedImportRef("a", "module", "a"),),
        )
    )

    with pytest.raises(UnsupportedSyntax, match="Circular typed module import"):
        link_typed_artifacts(a, {"a": a, "b": b})


def test_linked_bundle_round_trips_and_runs(tmp_path, capsys):
    lib = _unit(
        """#lang oort-core
enum Color { Blue, Red }
def make() -> Color { Red }
""",
        "lib",
    )
    main = _unit(
        """#lang oort-core
enum Color { Red }
print(Red)
""",
        "main",
        imports=(TypedImportRef("lib", "module", "lib"),),
    )
    program = build_typed_program((lib, main))

    path = tmp_path / "linked.obc"
    write_linked_bundle(program, path)
    loaded = read_linked_bundle(path)

    assert [decl.origin for decl in loaded.adt_decls] == [decl.origin for decl in program.adt_decls]
    raw = path.read_bytes()
    assert str(tmp_path).encode() not in raw

    TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert capsys.readouterr().out == "Red\n"


def test_build_typed_program_links_units_in_order():
    root = _unit(
        "#lang oort-core\nenum Color { Red }\nprint(Red)\n",
        "main",
        imports=(TypedImportRef("lib", "module", "lib"),),
    )
    lib = _unit("#lang oort-core\nenum Color { Blue }\n", "lib")

    program = build_typed_program((lib, root))

    assert [decl.origin for decl in program.adt_decls if decl.origin != "<core-prelude>"] == [
        "lib",
        "main",
    ]
