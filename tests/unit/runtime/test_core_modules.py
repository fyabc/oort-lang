#! /usr/bin/env python

"""Module imports for the `oort-core` dialect."""

from pathlib import Path

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def _write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(main: Path):
    compiler = get_compiler("NOT_EXIST -t eval")
    return compiler.run_file(main)


def _library(root: Path) -> None:
    _write(
        root,
        "lib.ort",
        "#lang oort-core\nval base: Int = 10\ndef add(a: Int, b: Int) -> Int { a + b }\n",
    )


def test_from_import_types_and_executes(tmp_path, run_file):
    _library(tmp_path)
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nfrom "./lib" import add, base\nprint(add(base, 2))\n',
    )
    assert run_file(main).stdout == "12\n"


def test_import_namespace_and_default_binding(tmp_path, run_file):
    _library(tmp_path)
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nimport "./lib"\nprint(lib.add(1, 2))\nprint(lib.base)\n',
    )
    assert run_file(main).stdout == "3\n10\n"


def test_import_alias_and_from_alias(tmp_path, run_file):
    _library(tmp_path)
    main = _write(
        tmp_path,
        "main.ort",
        "#lang oort-core\n"
        'import "./lib" as l\n'
        'from "./lib" import add as plus\n'
        "print(l.add(1, 1))\n"
        "print(plus(2, 3))\n",
    )
    assert run_file(main).stdout == "2\n5\n"


def test_imports_are_hoisted_before_function_bodies(tmp_path, run_file):
    _library(tmp_path)
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\ndef f() -> Int { lib.add(1, 2) }\nimport "./lib"\nprint(f())\n',
    )
    assert run_file(main).stdout == "3\n"


def test_imported_names_are_reexported(tmp_path, run_file):
    _library(tmp_path)
    _write(tmp_path, "mid.ort", '#lang oort-core\nfrom "./lib" import add\n')
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nfrom "./mid" import add\nprint(add(4, 5))\n',
    )
    assert run_file(main).stdout == "9\n"


def test_cross_module_argument_types_are_checked(tmp_path, caplog):
    _library(tmp_path)
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nfrom "./lib" import add\nprint(add(1, true))\n',
    )
    with pytest.raises(SystemExit):
        _run(main)
    assert "Expected Int, got Bool." in caplog.text


def test_missing_module_is_reported(tmp_path, caplog):
    main = _write(tmp_path, "main.ort", '#lang oort-core\nimport "./missing"\n')
    with pytest.raises(SystemExit):
        _run(main)
    assert "Cannot find module './missing'" in caplog.text


def test_missing_export_is_reported(tmp_path, caplog):
    _library(tmp_path)
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nfrom "./lib" import missing\n',
    )
    with pytest.raises(SystemExit):
        _run(main)
    assert "does not export 'missing'" in caplog.text


def test_core_cannot_import_object_module(tmp_path, caplog):
    _write(tmp_path, "obj.ort", "#lang oort-object\nval x = 1\n")
    main = _write(tmp_path, "main.ort", '#lang oort-core\nimport "./obj"\n')
    with pytest.raises(SystemExit):
        _run(main)
    assert "Cannot import a 'oort-object' module from an 'oort-core' module" in caplog.text


def test_core_cannot_import_native_module(tmp_path, caplog):
    main = _write(tmp_path, "main.ort", '#lang oort-core\nimport "math"\n')
    with pytest.raises(SystemExit):
        _run(main)
    assert "Native modules are not supported in oort-core imports yet." in caplog.text


def test_core_circular_import_is_reported(tmp_path, caplog):
    _write(tmp_path, "a.ort", '#lang oort-core\nimport "./b"\n')
    _write(tmp_path, "b.ort", '#lang oort-core\nimport "./a"\n')
    with pytest.raises(SystemExit):
        _run(tmp_path / "a.ort")
    assert "Circular import detected" in caplog.text


def test_imported_core_module_type_error_is_reported(tmp_path, caplog):
    _write(tmp_path, "bad.ort", "#lang oort-core\nvar x: Bool = 1\n")
    main = _write(tmp_path, "main.ort", '#lang oort-core\nimport "./bad"\n')
    with pytest.raises(SystemExit):
        _run(main)
    assert "TypeCheckError" in caplog.text


def test_object_import_of_core_module_requires_typed_subset(tmp_path, caplog):
    # `_library` has a top-level `val`, which the typed boundary does not carry.
    _library(tmp_path)
    main = _write(tmp_path, "main.ort", 'import "./lib"\n')
    with pytest.raises(CompilerError):
        _run(main)
    assert (
        "top-level declarations in modules executed across the object→core boundary" in caplog.text
    )


def test_class_with_inferred_methods_exported(tmp_path, run_file):
    # Method return types are inferred in the defining module and must carry
    # across the module boundary with the class.
    _write(
        tmp_path,
        "geom.ort",
        "#lang oort-core\n"
        "class Point {\n"
        "    val x: Int\n"
        "    val y: Int\n"
        "    def __init__(x: Int, y: Int) { this.x = x\n this.y = y }\n"
        "    def sum() { this.x + this.y }\n"
        "    def double_sum() { this.sum() * 2 }\n"
        "}\n",
    )
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nfrom "./geom" import Point\n'
        "val p = Point(2, 3)\nprint(p.sum(), p.double_sum())\n",
    )
    assert run_file(main).stdout == "5 10\n"
