#! /usr/bin/env python

"""End-to-end tests for the module loader."""

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
    compiler = get_compiler(["NOT_EXIST", "-t", "eval"])
    return compiler.run_file(main)


def test_import_binds_module_and_reads_attributes(tmp_path, run_file):
    _write(tmp_path, "lib.ort", "var value = 41\ndef get_value() { value + 1 }\n")
    main = _write(
        tmp_path,
        "main.ort",
        'import "./lib"\nprint(lib.get_value())\nprint(lib.value)\n',
    )

    assert run_file(main).stdout == "42\n41\n"


def test_import_alias_and_from_import_alias(tmp_path, run_file):
    _write(tmp_path, "lib.ort", "var value = 7\ndef get() { value }\n")
    main = _write(
        tmp_path,
        "main.ort",
        'import "./lib" as l\nfrom "./lib" import get as read, value as v\n'
        "print(l.get())\nprint(read())\nprint(v)\n",
    )

    assert run_file(main).stdout == "7\n7\n7\n"


def test_imports_are_hoisted_before_other_top_level_statements(tmp_path, run_file):
    _write(tmp_path, "dep.ort", 'print("dep")\n')
    main = _write(
        tmp_path,
        "main.ort",
        'print("before")\nimport "./dep"\nprint("after")\n',
    )

    assert run_file(main).stdout == "dep\nbefore\nafter\n"


def test_module_is_initialized_once_and_cached_by_canonical_path(tmp_path, run_file):
    _write(tmp_path, "dep.ort", 'print("loaded")\nvar value = 1\n')
    (tmp_path / "sub").mkdir()
    main = _write(
        tmp_path,
        "main.ort",
        'import "./dep" as a\nimport "./sub/../dep.ort" as b\nprint(a is b)\nprint(a.value)\n',
    )

    assert run_file(main).stdout == "loaded\ntrue\n1\n"


def test_relative_import_from_nested_module(tmp_path, run_file):
    _write(tmp_path, "shared.ort", "var value = 5\n")
    _write(tmp_path, "pkg/a.ort", 'import "../shared"\ndef get() { shared.value }\n')
    main = _write(tmp_path, "main.ort", 'import "./pkg/a"\nprint(a.get())\n')

    assert run_file(main).stdout == "5\n"


def test_module_globals_are_isolated(tmp_path, run_file):
    _write(tmp_path, "a.ort", 'var x = "A"\ndef who() { x }\n')
    main = _write(
        tmp_path,
        "main.ort",
        'import "./a"\nvar x = "B"\nprint(a.who())\nprint(x)\n',
    )

    assert run_file(main).stdout == "A\nB\n"


def test_methods_and_nested_functions_use_defining_module_globals(tmp_path, run_file):
    _write(
        tmp_path,
        "a.ort",
        """\
var x = "A"
class C {
    def who() { x }
}
def nested() {
    def inner() { x }
    inner()
}
""",
    )
    main = _write(
        tmp_path,
        "main.ort",
        'import "./a"\nvar x = "B"\nprint(a.C().who())\nprint(a.nested())\n',
    )

    assert run_file(main).stdout == "A\nA\n"


def test_imported_names_are_reexported(tmp_path, run_file):
    _write(tmp_path, "b.ort", "var value = 9\n")
    _write(tmp_path, "a.ort", 'import "./b"\n')
    main = _write(
        tmp_path,
        "main.ort",
        'import "./a"\nfrom "./a" import b\nprint(a.b.value)\nprint(b.value)\n',
    )

    assert run_file(main).stdout == "9\n9\n"


def test_builtins_are_not_module_attributes(tmp_path, caplog):
    _write(tmp_path, "lib.ort", "var value = 1\n")
    main = _write(tmp_path, "main.ort", 'import "./lib"\nprint(lib.print)\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "has no attribute 'print'" in caplog.text


def test_module_top_level_redefinition_is_allowed(tmp_path, run_file):
    _write(tmp_path, "lib.ort", "var x = 1\nvar x = 2\n")
    main = _write(tmp_path, "main.ort", 'import "./lib"\nprint(lib.x)\n')

    assert run_file(main).stdout == "2\n"


def test_missing_module_reports_search_locations(tmp_path, caplog):
    main = _write(tmp_path, "main.ort", 'import "./missing"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "Cannot find module './missing'" in caplog.text
    assert "Searched:" in caplog.text


def test_missing_from_export_is_reported(tmp_path, caplog):
    _write(tmp_path, "lib.ort", "var value = 1\n")
    main = _write(tmp_path, "main.ort", 'from "./lib" import nope, value\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "does not export 'nope'" in caplog.text
    assert "'value'" not in caplog.text


def test_circular_import_is_reported(tmp_path, caplog):
    _write(tmp_path, "a.ort", 'import "./b"\n')
    _write(tmp_path, "b.ort", 'import "./a"\n')

    with pytest.raises(CompilerError):
        _run(tmp_path / "a.ort")
    assert "Circular import detected" in caplog.text
    assert "a.ort -> b.ort -> a.ort" in caplog.text


def test_cycle_through_entry_file_is_reported(tmp_path, caplog):
    main = _write(tmp_path, "main.ort", 'import "./a"\n')
    _write(tmp_path, "a.ort", 'import "./main"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "Circular import detected" in caplog.text
    assert "main.ort -> a.ort -> main.ort" in caplog.text


def test_imported_module_compile_error_points_at_module(tmp_path, caplog):
    module = _write(tmp_path, "broken.ort", "var =\n")
    main = _write(tmp_path, "main.ort", 'import "./broken"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert str(module) in caplog.text
    assert "OortSyntaxError" in caplog.text
    assert "compilation failed" in caplog.text


def test_imported_module_runtime_error_points_at_module(tmp_path, caplog):
    module = _write(tmp_path, "broken.ort", "print(undefined_name)\n")
    main = _write(tmp_path, "main.ort", 'import "./broken"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert str(module) in caplog.text
    assert "OortNameError" in caplog.text


def test_cross_dialect_imports_are_rejected(tmp_path, caplog):
    _write(tmp_path, "core.ort", "#lang oort-core\nprint(1)\n")
    main = _write(tmp_path, "main.ort", 'import "./core"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "Cannot import a 'oort-core' module from an 'oort-object' module" in caplog.text


def test_core_entry_rejects_imports(tmp_path, caplog):
    _write(tmp_path, "lib.ort", "var value = 3\n")
    main = _write(tmp_path, "main.ort", '#lang oort-core\nimport "./lib"\n')

    with pytest.raises(SystemExit):
        _run(main)
    assert "Imports are not supported in oort-core yet." in caplog.text


def test_imported_core_module_is_type_checked(tmp_path, caplog):
    _write(tmp_path, "core.ort", "#lang oort-core\nvar value: Bool = 1\n")
    main = _write(tmp_path, "main.ort", 'import "./core"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "TypeCheckError" in caplog.text
    assert "compilation failed" in caplog.text


def test_explicit_oort_object_dialect_in_module(tmp_path, run_file):
    _write(tmp_path, "lib.ort", "#lang oort-object\nvar value = 3\n")
    main = _write(tmp_path, "main.ort", 'import "./lib"\nprint(lib.value)\n')

    assert run_file(main).stdout == "3\n"


def test_import_inside_function_is_rejected(tmp_path, caplog):
    main = _write(
        tmp_path,
        "main.ort",
        'def load() { import "./lib" }\n',
    )

    with pytest.raises(SystemExit):
        _run(main)
    assert "Imports are only allowed at module top level." in caplog.text


def test_import_from_string_uses_cwd(tmp_path, monkeypatch, capsys):
    _write(tmp_path, "lib.ort", "var value = 11\n")
    monkeypatch.chdir(tmp_path)
    compiler = get_compiler(["NOT_EXIST", "-t", "eval"])

    compiler.run_string('import "./lib"\nprint(lib.value)\n')

    assert capsys.readouterr().out == "11\n"


def test_module_path_option_is_used(tmp_path, capsys):
    libs = tmp_path / "libs"
    _write(libs, "extra.ort", "var value = 13\n")
    main = _write(tmp_path, "main.ort", 'import "extra"\nprint(extra.value)\n')

    compiler = get_compiler(["NOT_EXIST", "-t", "eval", "--module-path", str(libs)])
    compiler.run_file(main)

    assert capsys.readouterr().out == "13\n"


def test_module_path_option_is_required_for_external_module(tmp_path, caplog):
    libs = tmp_path / "libs"
    _write(libs, "extra.ort", "var value = 13\n")
    main = _write(tmp_path, "main.ort", 'import "extra"\n')

    with pytest.raises(CompilerError):
        _run(main)
    assert "Cannot find module 'extra'" in caplog.text
