#! /usr/bin/env python

"""Object -> core boundary prototype (design 17 B1)."""

from pathlib import Path

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler

CORE_LIB = """\
#lang oort-core

print("core init")

def add(a: Int, b: Int) -> Int { a + b }

def total(xs: List[Int]) -> Int {
    var sum: Int = 0
    for x in xs { sum = sum + x }
    sum
}

def doubled_total(xs: List[Int]) -> Int { total(xs) * 2 }

def pair(a: Int, b: String) -> Tuple[Int, String] { (a, b) }

def identity(xs: List[Int]) -> List[Int] { xs }

def ping() -> Unit { print("pong") }

def dict_score(d: Dict[String, Int]) -> Int { d["a"] + len(d) }

def set_count(s: Set[Int]) -> Int { len(s) }
"""


def _write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("target", ["eval", "vm"])
def test_object_imports_core_module(tmp_path, run_file, target):
    _write(tmp_path, "lib.ort", CORE_LIB)
    main = _write(
        tmp_path,
        "main.ort",
        """\
#lang oort-object

from "./lib" import add, total, doubled_total, pair, identity, ping, dict_score, set_count
import "./lib"

print(add(2, 3))
print(lib.add(4, 5))
print(total([1, 2, 3, 4]))
print(doubled_total([1, 2, 3, 4]))
print(pair(7, "x"))
val xs = [1, 2]
val ys = identity(xs)
xs[0] = 99
print(ys[0], xs[0])
print(ping())
print(dict_score({: "a": 10, "b": 20 :}))
print(set_count({. 1, 2, 2 .}))
""",
    )

    result = run_file(main, target=target)
    assert result.stdout == ("core init\n5\n9\n10\n20\n(7, x)\n1 99\npong\nnull\n12\n2\n")


@pytest.mark.parametrize("target", ["eval", "vm"])
def test_boundary_copies_adts_with_module_origin(tmp_path, run_file, target):
    _write(
        tmp_path,
        "a.ort",
        """#lang oort-core
enum Shape { Circle(radius: Int) }
def make(r: Int) -> Shape { Circle(r) }
def area(s: Shape) -> Int { match s { Circle(r) => r * r * 3 } }
""",
    )
    _write(
        tmp_path,
        "b.ort",
        """#lang oort-core
enum Shape { Square(side: Int) }
def make(side: Int) -> Shape { Square(side) }
def area(s: Shape) -> Int { match s { Square(s) => s * s } }
""",
    )
    main = _write(
        tmp_path,
        "main.ort",
        """#lang oort-object
import "./a"
import "./b"
val sa = a.make(2)
val sb = b.make(4)
print(sa, sb)
print(a.area(sa), b.area(sb))
""",
    )

    assert run_file(main, target=target).stdout == "Circle(2) Square(4)\n12 16\n"


@pytest.mark.parametrize("target", ["eval", "vm"])
def test_boundary_core_module_can_import_core(tmp_path, run_file, target):
    _write(
        tmp_path,
        "math.ort",
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
    )
    _write(
        tmp_path,
        "lib.ort",
        '#lang oort-core\nfrom "./math" import add\ndef calc(n: Int) -> Int { add(n, 1) }\n',
    )
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-object\nfrom "./lib" import calc\nprint(calc(41))\n',
    )

    assert run_file(main, target=target).stdout == "42\n"


def test_boundary_guard_rejects_wrong_argument_type(tmp_path, caplog):
    _write(
        tmp_path,
        "lib.ort",
        "#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n",
    )
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-object\nfrom "./lib" import add\nprint(add("x", 1))\n',
    )

    compiler = get_compiler(["NOT_EXIST", "-t", "vm"])
    with pytest.raises(CompilerError):
        compiler.run_file(main)
    assert "Boundary guard failed for 'add' argument 0" in caplog.text


def test_core_to_object_import_remains_rejected(tmp_path, caplog):
    _write(tmp_path, "lib.ort", "#lang oort-object\ndef value() { 1 }\n")
    main = _write(
        tmp_path,
        "main.ort",
        '#lang oort-core\nfrom "./lib" import value\nprint(value())\n',
    )

    with pytest.raises(SystemExit):
        get_compiler(["NOT_EXIST", "-t", "vm"]).run_file(main)
    assert "Cannot import a 'oort-object' module from an 'oort-core' module" in caplog.text
