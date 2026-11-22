#! /usr/bin/env python

"""Cross-module type annotations for `oort-core` (OP 0025 increment A)."""

from pathlib import Path

import pytest

from tests.helpers import get_compiler

SHAPES = """\
#lang oort-core

interface Nameable {
    def label() -> String
}

class Shape < Nameable {
    val name: String

    def __init__(name: String) {
        this.name = name
    }

    def label() -> String {
        this.name
    }
}

class Labeled < Shape {
    val extra: Int

    def __init__(name: String, extra: Int) {
        super.__init__(name)
        this.extra = extra
    }
}

enum Color { Red, Green }

enum Tree[T] {
    Leaf(value: T),
    Branch(left: Tree[T], right: Tree[T])
}
"""


def _module(tmp_path: Path, name: str, source: str) -> Path:
    path = tmp_path / f"{name}.ort"
    path.write_text(source, encoding="utf-8")
    return path


def _run_main(tmp_path: Path, source: str, target: str = "eval") -> None:
    _module(tmp_path, "shapes", SHAPES)
    main = _module(tmp_path, "main", "#lang oort-core\n" + source)
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_file(main)


def _diagnostics(tmp_path: Path, source: str, caplog: pytest.LogCaptureFixture) -> str:
    _module(tmp_path, "shapes", SHAPES)
    main = _module(tmp_path, "main", "#lang oort-core\n" + source)
    compiler = get_compiler(["NOT_EXIST", "-t", "eval"])
    with pytest.raises(SystemExit):
        compiler.run_file(main)
    return caplog.text


def test_module_qualified_and_imported_class_types(tmp_path: Path, capsys) -> None:
    _run_main(
        tmp_path,
        """\
import "./shapes" as shapes
from "./shapes" import Shape
from "./shapes" import Shape as Form

val a: shapes.Shape = shapes.Shape("box")
val b: Shape = Shape("ball")
val c: Form = Form("alias")

def describe(s: Shape) -> String {
    s.label()
}

def apply(f: (Shape) -> String) -> String {
    f(Shape("fn"))
}

def first(items: List[Shape]) -> String {
    items[0].label()
}

print(a.label())
print(b.label())
print(c.label())
print(describe(a))
print(apply(do(s: Shape) -> String { s.label() }))
print(first([a, b]))
""",
    )
    assert capsys.readouterr().out == "box\nball\nalias\nbox\nfn\nbox\n"


def test_module_qualified_enum_type_and_constructor_values(tmp_path: Path, capsys) -> None:
    _run_main(
        tmp_path,
        """\
import "./shapes" as shapes
from "./shapes" import Red, Green

def paint(color: shapes.Color) -> String {
    match color {
        Red => "red",
        Green => "green"
    }
}

print(paint(Red))
print(paint(shapes.Green))
""",
    )
    assert capsys.readouterr().out == "red\ngreen\n"


def test_module_qualified_generic_enum_type(tmp_path: Path, capsys) -> None:
    _run_main(
        tmp_path,
        """\
import "./shapes" as shapes
from "./shapes" import Leaf

val tree: shapes.Tree[Int] = Leaf(7)
print(match tree { Leaf(v) => v, Branch(_, _) => 0 })
""",
    )
    assert capsys.readouterr().out == "7\n"


@pytest.mark.parametrize("target", ["eval", "vm"])
def test_cross_module_class_runs_on_both_backends(tmp_path: Path, capsys, target: str) -> None:
    _run_main(
        tmp_path,
        """\
from "./shapes" import Shape

def describe(s: Shape) -> String {
    s.label()
}

print(describe(Shape("both")))
""",
        target=target,
    )
    assert capsys.readouterr().out == "both\n"


@pytest.mark.parametrize("target", ["eval", "vm"])
def test_cross_module_base_class(tmp_path: Path, capsys, target: str) -> None:
    _run_main(
        tmp_path,
        """\
import "./shapes" as shapes

class Labeled < shapes.Shape {
    val extra: Int

    def __init__(name: String, extra: Int) {
        super.__init__(name)
        this.extra = extra
    }

    def total() -> Int { this.extra }
}

val s: shapes.Shape = Labeled("cross", 3)
print(s.label(), Labeled("x", 2).total())
""",
        target=target,
    )
    assert capsys.readouterr().out == "cross 2\n"


def test_imported_derived_class_keeps_inherited_members(tmp_path: Path, capsys) -> None:
    _run_main(
        tmp_path,
        """\
import "./shapes" as shapes

val item: shapes.Labeled = shapes.Labeled("tag", 4)
print(item.label(), item.extra)
""",
    )
    assert capsys.readouterr().out == "tag 4\n"


def test_imported_interface_type_and_implementation(tmp_path: Path, capsys) -> None:
    _run_main(
        tmp_path,
        """\
import "./shapes" as shapes

class Tagged < shapes.Nameable {
    val tag: String

    def __init__(tag: String) {
        this.tag = tag
    }

    def label() -> String {
        this.tag
    }
}

def show(item: shapes.Nameable) -> String {
    item.label()
}

val a: shapes.Nameable = shapes.Shape("shape")
val b: shapes.Nameable = Tagged("tagged")
print(show(a), show(b))
""",
    )
    assert capsys.readouterr().out == "shape tagged\n"


def test_interface_name_cannot_be_imported_as_a_value(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    text = _diagnostics(tmp_path, caplog=caplog, source='from "./shapes" import Nameable\n')
    assert "'Nameable' is a type-only export" in text
    assert "use 'shapes.Nameable' to name the type." in text


def test_enum_type_name_cannot_be_imported_as_a_value(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    text = _diagnostics(tmp_path, caplog=caplog, source='from "./shapes" import Color\n')
    assert "'Color' is a type-only export" in text
    assert "use 'shapes.Color' to name the type." in text


def test_type_only_hint_uses_existing_module_alias(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    text = _diagnostics(
        tmp_path,
        caplog=caplog,
        source='import "./shapes" as s\nfrom "./shapes" import Color\n',
    )
    assert "use 's.Color' to name the type." in text


def test_missing_type_export_is_reported(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    text = _diagnostics(
        tmp_path,
        caplog=caplog,
        source='import "./shapes" as shapes\nval x: shapes.Missing = 1\n',
    )
    assert "Module 'shapes' does not export type 'Missing'." in text


def test_value_export_is_not_a_type(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    text = _diagnostics(
        tmp_path,
        caplog=caplog,
        source='import "./shapes" as shapes\nval x: shapes.Red = shapes.Red\n',
    )
    assert "Module 'shapes' exports 'Red' as a value, not a type." in text


def test_imported_class_type_is_not_redeclarable(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    text = _diagnostics(
        tmp_path,
        caplog=caplog,
        source='from "./shapes" import Shape\nclass Shape { }\n',
    )
    assert "Type name 'Shape' is already declared or reserved." in text


def test_qualified_non_generic_enum_rejects_type_arguments(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    text = _diagnostics(
        tmp_path,
        caplog=caplog,
        source='import "./shapes" as shapes\nval c: shapes.Color[Int] = shapes.Red\n',
    )
    assert "Enum 'shapes.Color' does not take type arguments." in text


def test_qualified_value_requires_module_import(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    text = _diagnostics(tmp_path, caplog=caplog, source="val c: shapes.Color = 1\n")
    assert "Unknown module 'shapes' in a type annotation." in text
