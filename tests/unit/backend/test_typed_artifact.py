#! /usr/bin/env python

"""Typed module artifacts (v12) and the link-time loader (design 19)."""

import dataclasses
import json
import subprocess
import sys

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
from oort_lang.bytecode.typed_cache import TypedArtifactCache
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.diagnostics.syntax_errors import UnsupportedSyntax
from oort_lang.hir import lower_typed_module
from oort_lang.hir.typed_link import TypedImportRef, TypedUnit
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.semantics.core.prelude import inject_core_prelude
from oort_lang.source.input_info import StringInputInfo
from tests.helpers import REPO_ROOT, get_compiler


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


def test_artifact_round_trip_keeps_big_int_literals(tmp_path):
    unit = _unit(
        "#lang oort-core\nprint(9223372036854775808, -9223372036854775809)\n",
        "big",
    )
    path = tmp_path / "big.obc"
    write_typed_artifact(build_typed_artifact(unit), path)

    loaded = read_typed_artifact(path)

    constants = [value for value in loaded.program.main.constants if isinstance(value, int)]
    assert 9223372036854775808 in constants
    # Negative literals lower to a positive constant plus NEG_I.
    assert 9223372036854775809 in constants


def test_v12_and_v10_artifacts_do_not_cross_read(tmp_path):
    unit = _unit("#lang oort-core\nprint(1)\n", "solo")
    artifact = build_typed_artifact(unit)
    v12_path = tmp_path / "v12.obc"
    write_typed_artifact(artifact, v12_path)

    dynamic_source = "#lang oort-core\ndef one() -> Int { 1 }\nprint(one())\n"
    v10_path = tmp_path / "v10.obc"
    write_typed_obc(
        compile_typed_module(lower_typed_module(_check(dynamic_source, "v6.ort"))),
        v10_path,
    )

    with pytest.raises(ObcError, match="unsupported typed module artifact version 10"):
        read_typed_artifact(v10_path)
    with pytest.raises(ObcError, match="unsupported typed bytecode version 12"):
        read_typed_obc(v12_path)


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


def test_link_artifacts_rejects_function_collision():
    source = "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n"
    a = _unit(source, "a")
    b = _unit(source, "b")
    root = _unit(
        "#lang oort-core\nprint(1)\n",
        "main",
        imports=(
            TypedImportRef("a", "module", "a"),
            TypedImportRef("b", "module", "b"),
        ),
    )

    with pytest.raises(UnsupportedSyntax, match="Typed function name collision: 'add'"):
        build_typed_program((a, b, root))


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


def _path_unit(tmp_path, source: str, module_id: str, imports=()) -> TypedUnit:
    path = tmp_path / f"{module_id}.ort"
    path.write_text(source, encoding="utf-8")
    unit = _unit(source, module_id, imports)
    unit.path = path
    return unit


def test_artifact_cache_hits_and_rebuilds_dependents(tmp_path, monkeypatch):
    lib_source = "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n"
    lib = _path_unit(tmp_path, lib_source, "lib")
    main = _path_unit(
        tmp_path,
        "#lang oort-core\nprint(1)\n",
        "main",
        imports=(TypedImportRef("lib", "module", "lib"),),
    )
    cache = TypedArtifactCache(tmp_path / "cache")

    import oort_lang.bytecode.typed_artifact as artifact_module

    real_build = artifact_module.build_typed_artifact
    calls: list[str] = []

    def counting(unit, origins=None):
        calls.append(unit.module_id)
        return real_build(unit, origins)

    monkeypatch.setattr(artifact_module, "build_typed_artifact", counting)

    build_typed_program((lib, main), cache)
    assert set(calls) == {"lib", "main"}
    assert len(list((tmp_path / "cache").rglob("*.obc"))) == 2

    calls.clear()
    build_typed_program((lib, main), cache)
    assert calls == []

    changed_impl = _path_unit(
        tmp_path,
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { b + a }\n",
        "lib",
    )
    build_typed_program((changed_impl, main), cache)
    assert set(calls) == {"lib"}

    calls.clear()
    changed_api = _path_unit(
        tmp_path,
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\ndef extra() -> Int { 1 }\n",
        "lib",
    )
    build_typed_program((changed_api, main), cache)
    assert set(calls) == {"lib", "main"}


def test_artifact_cache_layout_stats_clean_and_corruption(tmp_path):
    lib = _path_unit(
        tmp_path,
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        "lib",
    )
    main = _path_unit(
        tmp_path,
        "#lang oort-core\nprint(1)\n",
        "main",
        imports=(TypedImportRef("lib", "module", "lib"),),
    )
    cache = TypedArtifactCache(tmp_path / "cache")
    build_typed_program((lib, main), cache)

    entries = sorted((tmp_path / "cache" / "v12" / "abi1").rglob("*.obc"))
    assert len(entries) == 2
    stats = cache.stats()
    assert stats.entries == 2
    assert stats.size_bytes > 0

    entries[0].write_bytes(b"")
    build_typed_program((lib, main), cache)
    assert cache.stats().entries == 2

    assert cache.clean() == 4  # two artifacts plus their manifests
    assert cache.stats().entries == 0


def test_cache_manifest_and_size_limit(tmp_path):
    lib = _path_unit(
        tmp_path,
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        "lib",
    )
    main = _path_unit(
        tmp_path,
        "#lang oort-core\nprint(1)\n",
        "main",
        imports=(TypedImportRef("lib", "module", "lib"),),
    )
    cache = TypedArtifactCache(tmp_path / "cache", max_size=1)
    build_typed_program((lib, main), cache)

    assert cache.stats().entries == 1
    manifests = list((tmp_path / "cache" / "v12" / "abi1").rglob("*.json"))
    assert len(manifests) == 1
    data = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert data["schema"] == "oort-cache-v1"
    assert data["module_id"] in {"lib", "main"}
    assert isinstance(data["dependencies"], dict)


def test_cache_entry_lock_is_single_flight(tmp_path):
    unit = _path_unit(
        tmp_path,
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        "lib",
    )
    cache = TypedArtifactCache(tmp_path / "cache")
    with cache.entry_lock(unit, {}) as status:
        assert status == "owned"
        lock_files = list((tmp_path / "cache" / "locks").glob("*.lock"))
        assert len(lock_files) == 1
    assert not list((tmp_path / "cache" / "locks").glob("*.lock"))


_CACHE_WORKER = """
import os
import sys
import time

from tests.helpers import get_compiler
import oort_lang.bytecode.typed_artifact as artifacts

log = sys.argv[3]
real = artifacts.build_typed_artifact

def counting(unit, origins=None):
    descriptor = os.open(log, os.O_APPEND | os.O_CREAT | os.O_WRONLY)
    os.write(descriptor, (unit.module_id + "\\n").encode("utf-8"))
    os.close(descriptor)
    time.sleep(0.1)
    return real(unit, origins)

artifacts.build_typed_artifact = counting
compiler = get_compiler(["NOT_EXIST", "-t", "tvm", "--cache-dir", sys.argv[2]])
compiler.run_file(sys.argv[1])
"""


def test_cache_concurrent_processes_compile_once(tmp_path):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import add\nprint(add(2, 3))\n',
        encoding="utf-8",
    )
    cache_dir = tmp_path / "cache"
    log = tmp_path / "builds.txt"

    processes = [
        subprocess.Popen(
            [sys.executable, "-c", _CACHE_WORKER, str(main), str(cache_dir), str(log)],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        for _ in range(8)
    ]
    results = [process.communicate(timeout=120) for process in processes]

    assert all(process.returncode == 0 for process in processes), [stderr for _, stderr in results]
    assert all(stdout == "5\n" for stdout, _ in results)
    builds = log.read_text(encoding="utf-8").split()
    assert sorted(builds) == ["lib", "main"]
    assert not list((tmp_path / "cache" / "locks").glob("*.lock"))
    assert len(list(cache_dir.rglob("*.obc"))) == 2


def test_cache_env_precedence_and_no_cache(tmp_path, monkeypatch, capsys):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import add\nprint(add(2, 3))\n',
        encoding="utf-8",
    )
    env_dir = tmp_path / "env-cache"
    flag_dir = tmp_path / "flag-cache"
    disabled_dir = tmp_path / "disabled-cache"
    monkeypatch.setenv("OORT_CACHE_DIR", str(env_dir))

    def run(*extra: str) -> None:
        compiler = get_compiler([*extra, "-t", "tvm", "NOT_EXIST", str(main)])
        compiler.run_file(main)
        assert capsys.readouterr().out == "5\n"

    run("--no-cache")
    assert not env_dir.exists()

    run()
    assert len(list(env_dir.rglob("*.obc"))) == 2

    run("--cache-dir", str(flag_dir))
    assert len(list(flag_dir.rglob("*.obc"))) == 2
    assert len(list(env_dir.rglob("*.obc"))) == 2

    run("--no-cache", "--cache-dir", str(disabled_dir))
    assert not disabled_dir.exists()


def test_cli_cache_dir_produces_reusable_artifacts(tmp_path, capsys):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import add\nprint(add(2, 3))\n',
        encoding="utf-8",
    )
    cache_dir = tmp_path / "cache"

    outputs = []
    for _ in range(2):
        compiler = get_compiler(["NOT_EXIST", "-t", "tvm", "--cache-dir", str(cache_dir)])
        compiler.run_file(main)
        outputs.append(capsys.readouterr().out)

    assert outputs == ["5\n", "5\n"]
    assert len(list(cache_dir.rglob("*.obc"))) == 2


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
