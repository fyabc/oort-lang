#! /usr/bin/env python

"""Differential + benchmark check for the Rust VM spike against the Python VM.

Differential: compile a curated set of programs (Phase 0 subset) to ``.obc``,
run them on both the Python VM (``-t vm``) and the Rust VM, compare stdout.

Benchmark: run the reference fib/loop/methods programs on the Rust VM several
times, take the median of the program-internal per-rep milliseconds, and compare
against the Python VM baseline.

Usage:
    uv run --frozen python scripts/rust_vm_check.py [--rust-bin PATH] [--repeat N]
"""

import argparse
import contextlib
import io
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from oort_lang.bytecode import (
    build_typed_artifacts,
    build_typed_program,
    compile_module,
    compile_typed_module,
    write_linked_bundle,
    write_typed_artifact,
    write_typed_obc,
)
from oort_lang.bytecode.serialize import write_obc
from oort_lang.bytecode.typed_vm import TypedCodeVM
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.diagnostics.runtime_errors import OortRuntimeError
from oort_lang.hir import lower_module, lower_typed_module
from oort_lang.hir.typed_link import TypedUnit, load_typed_units
from oort_lang.runtime.bytecode_vm import BytecodeVM
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.semantics.core.prelude import inject_core_prelude
from oort_lang.source.input_info import FileInputInfo
from tests.helpers import build_ast, get_compiler

DEFAULT_RUST_BIN = ROOT / "rust" / "target" / "release" / "oort-vm.exe"

# Curated differential programs within the Phase 0 subset (no closures/kwargs/
# collections/ADT). Each prints its result so stdout is comparable.
DIFF_PROGRAMS = {
    "fib": "def fib(n) { if n <= 1: return n\nfib(n-1)+fib(n-2) }\nprint(fib(15))\n",
    "loop": "var total = 0\nfor i in range(10000) { total = total + i }\nprint(total)\n",
    "globals_block": (
        "var g = 1\ndef f(a, b) { var x = a + b\nif x > 2 { return x * 2 }\nx }\n"
        "print(f(1, 2), f(2, 2))\nwhile g < 4 { g = g + 1 }\nprint(g)\n"
        "{ var g = 9\nprint(g) }\nprint(g)\n"
    ),
    "sign": (
        "def sign(n) { if n < 0 { return -1 }\nif n > 0 { return 1 }\n0 }\n"
        "print(sign(-2), sign(0), sign(3))\n"
    ),
    "counter": (
        "class Counter {\n"
        "    def __init__(start) { this.n = start }\n"
        "    def inc() { this.n = this.n + 1\nthis.n }\n"
        "    def get() { this.n }\n"
        "}\n"
        "val c = Counter(10)\nprint(c.get())\nprint(c.inc())\nc.n = 20\nprint(c.get())\n"
        "val bump = c.inc\nbump()\nprint(c.get())\n"
    ),
    "break_continue": (
        "var total = 0\nfor i in range(10) {\nif i == 2: continue\nif i == 5: break\n"
        "total = total + i\n}\nprint(total)\n"
        "var j = 0\nwhile j < 10 {\nj = j + 1\nif j == 3: continue\nif j == 6: break\n"
        "total = total + j\n}\nprint(total)\n"
    ),
    "arith": (
        "print(1 + 2 * 3, 7 / 2, 7 // 2, 7 % 2)\n"
        "print(-7 // 2, -7 % 2, 7 // -2, 7 % -2)\n"
        "print(1 < 2, 2 <= 2, 3 > 4, 1 == 1.0)\n"
    ),
    "big_int": (
        "def pow2(k) { var r = 1\nvar i = 0\nwhile i < k { r = r * 2\ni = i + 1 }\nr }\n"
        "var a = pow2(100)\n"
        "print(a)\n"
        "print(a // 3, a % 7)\n"
        "print((-a - 1) // 3, (-a - 1) % 3)\n"
        "print(a > pow2(99), -a < 0)\n"
        "print(pow2(53) + 1 == 9007199254740992.0, pow2(53) == 9007199254740992.0)\n"
        "var n = 9223372036854775808\nprint(n, n + n, ~n)\n"
        "print(1 == 1.0, 1 < 1.5)\n"
    ),
}

BENCH_PROGRAMS = {
    "fib": ROOT / "benchmarks" / "reference" / "programs" / "fib.ort",
    "loop": ROOT / "benchmarks" / "reference" / "programs" / "loop.ort",
    "methods": ROOT / "benchmarks" / "reference" / "programs" / "methods.ort",
}
BENCH_EXPECTED = {"fib": "6765", "loop": "199990000", "methods": "5000"}
# Python VM baseline (benchmarks/RESULTS.md, cross-language exec ms).
PYTHON_VM_BASELINE = {"fib": 324.2, "loop": 128.0, "methods": 119.2}


def python_vm_stdout(source: str) -> str:
    program = compile_module(lower_module(build_ast(source)))
    interpreter = ASTInterpreter(CompilerErrorHandler())
    vm = BytecodeVM(interpreter)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), interpreter.runtime.activate():
        vm.run(program)
    return buf.getvalue()


def compile_to_obc(source: str, path: Path) -> None:
    write_obc(compile_module(lower_module(build_ast(source))), path)


TYPED_DIFF_PROGRAMS = {
    "typed_fib": """#lang oort-core

def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}

print(fib(15))
""",
    "typed_loop": """#lang oort-core

def total(n: Int) -> Int {
    var sum: Int = 0
    var i: Int = 0
    while i < n {
        sum = sum + i
        i = i + 1
    }
    sum
}

print(total(10000))
""",
    "typed_early_return": """#lang oort-core

def sign(n: Int) -> Int {
    if n < 0 { return -1 }
    if n > 0 { return 1 }
    0
}

print(sign(-2), sign(0), sign(3))
""",
    "typed_mixed": """#lang oort-core

def average(a: Float, b: Float) -> Float {
    (a + b) / 2.0
}

def close(a: Float, b: Float) -> Bool {
    a - b < 0.001 and b - a < 0.001
}

print(average(1.0, 4.0), close(1.0, 1.0005))
""",
    "typed_mixed_compare": """#lang oort-core

def same(big: Int, f: Float) -> Bool { big == f }
def below(big: Int, f: Float) -> Bool { big < f }
def above(big: Int, f: Float) -> Bool { big > f }

print(same(9007199254740993, 9007199254740992.0))
print(same(9007199254740992, 9007199254740992.0))
print(below(9007199254740992, 9007199254740994.0))
print(above(9007199254740993, 9007199254740992.0))
""",
    "typed_float_display": """#lang oort-core

def show() -> Unit {
    print(2.0)
    print(-0.0)
    print(0.06)
    print(1e20)
    print(1e-20)
    print(1e-5)
}

show()
""",
    "typed_string": """#lang oort-core

def greet(name: String) -> String {
    "Hello, " + name
}

def before(a: String, b: String) -> Bool { a < b }

print(greet("Oort"))
print(len("abc"), len(""))
print("a" < "b", "a" == "a", "a" != "b")
print(before("b", "a"))
""",
    "typed_collections": """#lang oort-core

def first(xs: List[Int]) -> Int { xs[0] }

def pair(a: Int, b: String) -> Tuple[Int, String] { (a, b) }

print([1, 2, 3])
print(len([1, 2, 3]))
print(first([4, 5]))
print(pair(7, "x"))
print([1, 2] == [1, 2], [1, 2] != [1, 3])
""",
    "typed_adts": """#lang oort-core

enum Shape {
    Circle(radius: Int),
    Rect(width: Int, height: Int),
    Empty,
}

enum Tree {
    Leaf(value: Int),
    Node(left: Tree, right: Tree),
}

def area(shape: Shape) -> Int {
    match shape {
        Circle(r) => r * r * 3,
        Rect(w, h) => w * h,
        Empty => 0,
    }
}

def tree_sum(tree: Tree) -> Int {
    match tree {
        Leaf(value) => value,
        Node(left, right) => tree_sum(left) + tree_sum(right),
    }
}

print(area(Circle(2)), area(Rect(3, 4)), area(Empty))
print(tree_sum(Node(Leaf(1), Node(Leaf(2), Leaf(3)))))
print(Circle(2) == Circle(2), Circle(2) == Circle(3))
print(Circle(2))
""",
    "typed_patterns": """#lang oort-core

enum Shape {
    Point,
    Line(x: Int),
}

def describe(shape: Shape) -> String {
    match shape {
        Point => "point",
        Line(0) => "zero",
        Line(x) if x < 0 => "negative",
        Line(_) => "line",
    }
}

def classify(n: Int) -> String {
    match n {
        0 => "zero",
        1 | 2 | 3 => "small",
        x if x < 0 => "negative",
        _ => "large",
    }
}

def at_origin(p: Tuple[Int, Int]) -> Bool {
    match p {
        (0, 0) => true,
        _ => false,
    }
}

def classify_text(s: String) -> Int {
    match s {
        "a" => 1,
        "b" => 2,
        _ => 0,
    }
}

def flag(b: Bool) -> Int {
    match b {
        true => 1,
        false => 0,
    }
}

def pair(p: Tuple[Int, String]) -> Bool {
    match p {
        (0, "x") => true,
        _ => false,
    }
}

print(describe(Point), describe(Line(0)), describe(Line(-2)), describe(Line(3)))
print(classify(0), classify(2), classify(-1), classify(9))
print(at_origin((0, 0)), at_origin((0, 1)))
print(classify_text("a"), classify_text("z"), flag(true), flag(false))
print(pair((0, "x")), pair((1, "x")))
""",
    "typed_generic_adts": """#lang oort-core

enum Maybe[T] {
    Just(value: T),
    Nothing,
}

def unwrap(value: Maybe[Int], fallback: Int) -> Int {
    match value {
        Just(v) => v,
        Nothing => fallback,
    }
}

print(unwrap(Just(7), 0))
print(unwrap(Nothing, 9))
print(unwrap(Just(3), 9) + unwrap(Nothing, 4))
""",
    "typed_sets_dicts": """#lang oort-core

def dict_total(items: Dict[String, Int]) -> Int {
    var total: Int = 0
    for key in items { total = total + items[key] }
    total
}

def set_total(items: Set[Int]) -> Int {
    var total: Int = 0
    for item in items { total = total + item }
    total
}

def tuple_key(items: Dict[Tuple[Int, Bool], String]) -> String { items[(1, true)] }

def float_key(items: Dict[Float, String]) -> String { items[1.5] }

print({: "a": 1, "b": 2 :}["b"], len({: "a": 1, "b": 2 :}))
print(dict_total({: "a": 1, "b": 2 :}))
print(set_total({. 2, 4, 6 .}), len({. 2, 4, 6 .}))
print({: "a": 1 :} == {: "a": 1 :}, {. 1, 2 .} == {. 2, 1 .})
print({: "x": (1, true) :})
print(tuple_key({: (1, true): "yes", (2, false): "no" :}))
print(float_key({: 1.5: "ok", 2.5: "no" :}))
print(len({. (1, 2), (2, 3), (1, 2) .}))
""",
    "typed_iteration": """#lang oort-core

def total(xs: List[Int]) -> Int {
    var sum: Int = 0
    for x in xs { sum = sum + x }
    sum
}

def tuple_total(xs: Tuple[Int, Int, Int]) -> Int {
    var sum: Int = 0
    for x in xs { sum = sum + x }
    sum
}

def last_char(s: String) -> String {
    var out: String = ""
    for ch in s { out = ch }
    out
}

print(total([1, 2, 3, 4]))
print(tuple_total((5, 6, 7)))
print(last_char("Oort"))
""",
    "typed_big_int": """#lang oort-core

def pow2(k: Int) -> Int {
    var result: Int = 1
    var i: Int = 0
    while i < k { result = result * 2; i = i + 1 }
    result
}

print(pow2(100))
print(pow2(100) // 3, pow2(100) % 7)
print((-pow2(100) - 1) // 3, (-pow2(100) - 1) % 3)
print(pow2(100) > pow2(99), -pow2(100) < 0)
print(pow2(53) + 1 == 9007199254740992.0)
print(pow2(53) == 9007199254740992.0)
print(9223372036854775808, -9223372036854775809)
""",
    "typed_function_values": """#lang oort-core

def inc(x: Int) -> Int { x + 1 }
def dec(x: Int) -> Int { x - 1 }

def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }
def pick(flag: Bool) -> (Int) -> Int { if flag { inc } else { dec } }
def local() -> Int { val f: (Int) -> Int = inc; f(10) }

def sum_apply(fs: List[(Int) -> Int], x: Int) -> Int {
    var total: Int = 0
    for f in fs { total = total + f(x) }
    total
}

def dispatch(op: String, x: Int) -> Int {
    val table: Dict[String, (Int) -> Int] = {: "inc": inc, "dec": dec :}
    val f: (Int) -> Int = table[op]
    f(x)
}

def with_lambda() -> Int {
    val double: (Int) -> Int = do(x: Int) -> Int { x * 2 }
    double(21)
}

def lambda_arg() -> Int {
    apply(do(x: Int) -> Int { x + 10 }, 5)
}

def lambda_in_list() -> Int {
    val fs: List[(Int) -> Int] = [do(x: Int) -> Int { x - 1 }, inc]
    var total: Int = 0
    for f in fs { total = total + f(10) }
    total
}

def nested_lambda() -> Int {
    val f: (Int) -> Int = do(x: Int) -> Int { apply(do(y: Int) -> Int { y * 3 }, x) }
    f(4)
}

print(apply(inc, 1), apply(dec, 1))
print(apply(pick(true), 2), apply(pick(false), 2))
print(local())
print(sum_apply([inc, dec], 10))
print(dispatch("inc", 6), dispatch("dec", 6))
print(with_lambda(), lambda_arg(), lambda_in_list(), nested_lambda())
""",
    "typed_capturing_closures": """#lang oort-core

def make_adder(n: Int) -> (Int) -> Int {
    do(x: Int) -> Int { x + n }
}

def use_adder() -> Int {
    val add10 = make_adder(10)
    add10(5)
}

def loop_capture() -> Int {
    var total = 0
    for i in [10, 20, 30] {
        val g = do(x: Int) -> Int { x + i }
        total = total + g(1)
    }
    total
}

def nested(a: Int) -> (Int) -> (Int) -> Int {
    do(b: Int) -> (Int) -> Int {
        do(c: Int) -> Int { a + b + c }
    }
}

def use_nested() -> Int {
    val step = nested(100)
    val partial = step(20)
    partial(3)
}

def shadow() -> Int {
    val n = 100
    val f = do(n: Int) -> Int { n * 2 }
    f(7) + n
}

def counter() -> () -> Int {
    var n = 0
    do() -> Int { n = n + 1; n }
}

def use_counter() -> Int {
    val c = counter()
    c() + c() + c()
}

def reassign_after_capture() -> Int {
    var k = 1
    val f = do(x: Int) -> Int { x + k }
    k = 2
    f(10)
}

def make_acc() -> Int {
    var sum = 0
    val add = do(v: Int) -> Unit { sum = sum + v }
    add(1)
    add(20)
    add(300)
    sum
}

print(use_adder(), loop_capture(), use_nested(), shadow())
print(use_counter(), reassign_after_capture(), make_acc())
""",
    "typed_collection_surface": """#lang oort-core

def adjust() -> Int {
    var xs: List[Int] = [1, 2]
    var alias: List[Int] = xs
    xs[0] = 9
    alias[0]
}

def mapping() -> Int {
    var d: Dict[String, Int] = {: "a": 1 :}
    d["b"] = 2
    d["a"] + d["b"]
}

def snapshot() -> Int {
    var xs: List[Int] = [1, 2]
    var sum: Int = 0
    for x in xs { xs[0] = 99; sum = sum + x }
    sum
}

print(2 in [1, 2], 3 !in [1, 2], "bc" in "abcd", "a" in {: "a": 1 :})
print(2 in {. 1, 2 .}, 2 in (1, 2))
print(adjust(), mapping(), snapshot())
print([1, 2, 3, 4][1:3], [1, 2, 3, 4][-2:], [1, 2, 3, 4][:2], [1, 2, 3, 4][3:1])
print("abcd"[1:3], "abcd"[-2:])
print((1, "a", true)[1:])
print({. 1, 2 .} | {. 2, 3 .}, {. 1, 2 .} & {. 2, 3 .})
print({. 1, 2 .} - {. 2 .}, {. 1, 2 .} ^ {. 2, 3 .})
""",
    "typed_set_relations": """#lang oort-core

def relations() -> Unit {
    val a: Set[Int] = {. 1, 2 .}
    val b: Set[Int] = {. 1, 2, 3 .}
    val c: Set[Int] = {. 1, 2 .}
    val empty: Set[Int] = {. .}
    print(a <= b, a < b, b >= a, b > a)
    print(a <= c, a < c, a >= c, a > c)
    print({. 1 .} < a, {. 9 .} <= a, {. 9 .} < a)
    print(empty <= a, empty < a, a >= empty, a > empty)
}

relations()
""",
    "typed_ordering": """#lang oort-core

def ordering() -> Unit {
    val a: List[Int] = [3, 1, 2]
    val b: List[Int] = [1, 2]
    val c: List[Int] = [1, 2, 3]
    val empty: List[Int] = []
    print(sorted(a), a)
    print(b + [3], b + empty)
    print(b < c, b <= b, b > [1], b > b)
    print(["b", "a"] < ["a"], empty < b, empty == empty)
    print([1.5, 0.5] < [0.5, 2.0])
    print(sorted(["b", "a", "c"]))
}

ordering()
""",
    "typed_top_level": """#lang oort-core

def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }

val name: String = "Oort"
val double: (Int) -> Int = do(x: Int) -> Int { x * 2 }
var count: Int = 0

def bump() -> Int {
    count = count + 1
    count
}

count = 10
print(name, count)
print(apply(double, 3))
print(bump(), bump(), count)
""",
    "typed_currying": """#lang oort-core

val add: Int -> Int -> Int = do(a: Int) -> Int -> Int {
    do(b: Int) -> Int { a + b }
}

print(add(2)(3))
""",
    "typed_generic_functions": """#lang oort-core

def id[T](x: T) -> T { x }
def wrap[T](x: T) -> List[T] { [x, x] }
def pair[A, B](a: A, b: B) -> Tuple[A, B] { (a, b) }
def count_all[T](xs: List[T]) -> Int {
    if len(xs) == 0 { 0 } else { 1 + count_all(xs[1:]) }
}

print(id(true), id(2.5))
print(wrap(7), wrap("a"))
print(pair(1, "x"), pair(false, 2.5))
print(count_all([1, 2, 3]), count_all(["a", "b"]))
""",
}


# Multi-module typed cases: (dependency sources, root source). They exercise
# v13 artifact linking (imported constructors, same-named ADTs) through kind=2.
# Programs that fail at runtime. Both VMs must fail, and the innermost Rust
# frame must point at the same source line as the Python exception position.
# Messages are not compared: Python surfaces host exception text.
DYNAMIC_ERROR_PROGRAMS = {
    "div_zero": (
        "def bad(x) { 10 // x }\nprint(bad(0))\n",
        "bad",
        1,
    ),
}

TYPED_ERROR_PROGRAMS = {
    "typed_div_zero": (
        "#lang oort-core\n"
        "\n"
        "def bad(x: Int) -> Int { 10 // x }\n"
        "\n"
        "def run() -> Int { bad(0) }\n"
        "\n"
        "print(run())\n",
        "bad",
        3,
    ),
}

TYPED_MODULE_DIFF_PROGRAMS = {
    "typed_imported_ctors": (
        {
            "lib.ort": """#lang oort-core
enum Color { Red, Green }
def make() -> Color { Red }
""",
        },
        """#lang oort-core
import "./lib"
from "./lib" import Red, Green, make
def paint(color: lib.Color) -> Int { match color { Red => 1, Green => 2 } }
print(paint(make()), paint(Green))
""",
    ),
    "typed_same_named_adts": (
        {
            "a.ort": """#lang oort-core
enum Color { Red }
def make_a() -> Color { Red }
def area_a(color: Color) -> Int { match color { Red => 1 } }
""",
            "b.ort": """#lang oort-core
enum Color { Blue }
def make_b() -> Color { Blue }
def area_b(color: Color) -> Int { match color { Blue => 2 } }
""",
        },
        """#lang oort-core
import "./a"
import "./b"
print(a.area_a(a.make_a()), b.area_b(b.make_b()))
""",
    ),
    "typed_module_lambdas": (
        {
            "lib.ort": """#lang oort-core
def twice(f: (Int) -> Int, x: Int) -> Int { f(f(x)) }
def lib_lambda() -> Int { twice(do(v: Int) -> Int { v + 3 }, 4) }
""",
        },
        """#lang oort-core
from "./lib" import twice, lib_lambda
def main_lambda() -> Int { twice(do(v: Int) -> Int { v * 2 }, 5) }
print(lib_lambda(), main_lambda())
""",
    ),
}


def python_typed_stdout(source: str) -> str:
    typed = lower_typed_module(build_ast(source))
    program = compile_typed_module(typed)
    interpreter = ASTInterpreter(CompilerErrorHandler())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), interpreter.runtime.activate():
        TypedCodeVM(interpreter).run(program)
    return buf.getvalue()


def compile_to_typed_obc(source: str, path: Path) -> None:
    typed = lower_typed_module(build_ast(source))
    write_typed_obc(compile_typed_module(typed), path)


def compile_to_linked_bundle(source: str, path: Path) -> None:
    ast = build_ast(source)
    module = lower_typed_module(ast)
    unit = TypedUnit(
        None,
        "<string>",
        ast,
        module,
        {function.hir.name for function in module.functions},
        {constructor.name for decl in module.adt_decls for constructor in decl.constructors},
        {decl.name for decl in module.adt_decls},
    )
    write_linked_bundle(build_typed_program((unit,)), path)


def python_program_stdout(program) -> str:
    interpreter = ASTInterpreter(CompilerErrorHandler())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), interpreter.runtime.activate():
        TypedCodeVM(interpreter).run(program)
    return buf.getvalue()


def _frontend(main_path: Path):
    compiler = get_compiler("NOT_EXIST -t tvm")
    compiler._entry_dir = main_path.parent
    info = FileInputInfo(main_path)
    compiler.error_handler.register_input(info)
    dialect = compiler._resolve_dialect(info)
    assert dialect is not None
    parser, tokenized = compiler.prepare_parser(info)
    ast = compiler.build_ast(parser, info, dialect=dialect, tokenized=tokenized)
    assert ast is not None
    inject_core_prelude(ast)
    analyzer = compiler.make_semantic_analyzer(info, dialect)
    ast = compiler.semantic_analyze(ast, analyzer)
    assert ast is not None
    return compiler, ast, info


def compile_files_to_bundle(main_path: Path, out: Path):
    """Compile a multi-module core entry through the real frontend + linker."""

    compiler, ast, info = _frontend(main_path)
    program = compiler._compile_typed_entry(ast, info)
    write_linked_bundle(program, out)
    return program


def compile_files_to_artifacts(main_path: Path, out_dir: Path):
    """Write one v13 artifact per module; return (root_path, dependency_paths)."""

    compiler, ast, _info = _frontend(main_path)
    resolve = compiler._make_typed_resolver(main_path.parent)
    units = load_typed_units(ast, main_path, resolve)
    root, modules = build_typed_artifacts(units)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for module_id, artifact in modules.items():
        path = out_dir / f"{module_id.replace('/', '_')}.obc"
        write_typed_artifact(artifact, path)
        paths[module_id] = path
    root_path = paths[root.module_id]
    dependencies = [path for module_id, path in paths.items() if module_id != root.module_id]
    return root_path, dependencies


def rust_stdout(rust_bin: Path, obc: Path, link_deps: list[Path] | None = None) -> str:
    command = [str(rust_bin)]
    if link_deps is not None:
        command.append("--link")
    command.append(str(obc))
    if link_deps is not None:
        command.extend(str(path) for path in link_deps)
    proc = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"rust vm failed: {proc.stderr.strip()}")
    return proc.stdout


def differential(rust_bin: Path) -> bool:
    print("== differential (Rust VM vs Python VM, stdout) ==")
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for name, source in DIFF_PROGRAMS.items():
            obc = Path(tmp) / f"{name}.obc"
            compile_to_obc(source, obc)
            expected = python_vm_stdout(source)
            try:
                actual = rust_stdout(rust_bin, obc)
            except RuntimeError as e:
                print(f"  {name:16s} ERROR: {e}")
                ok = False
                continue
            if actual == expected:
                print(f"  {name:16s} OK")
            else:
                ok = False
                print(f"  {name:16s} MISMATCH\n    python={expected!r}\n    rust  ={actual!r}")
    return ok


def typed_differential(rust_bin: Path) -> bool:
    print("\n== typed differential (kind=2 bundles, Rust vs Python typed VM) ==")
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for name, source in TYPED_DIFF_PROGRAMS.items():
            obc = Path(tmp) / f"{name}.obc"
            compile_to_linked_bundle(source, obc)
            expected = python_typed_stdout(source)
            try:
                actual = rust_stdout(rust_bin, obc)
            except RuntimeError as e:
                print(f"  {name:20s} ERROR: {e}")
                ok = False
                continue
            if actual == expected:
                print(f"  {name:20s} OK")
            else:
                ok = False
                print(f"  {name:20s} MISMATCH\n    python={expected!r}\n    rust  ={actual!r}")

        for name, (dependencies, main_source) in TYPED_MODULE_DIFF_PROGRAMS.items():
            module_dir = Path(tmp) / name
            module_dir.mkdir()
            for filename, source in dependencies.items():
                (module_dir / filename).write_text(source, encoding="utf-8")
            main_path = module_dir / "main.ort"
            main_path.write_text(main_source, encoding="utf-8")
            obc = Path(tmp) / f"{name}.obc"
            try:
                expected = python_program_stdout(compile_files_to_bundle(main_path, obc))
                actual = rust_stdout(rust_bin, obc)
            except (RuntimeError, SystemExit) as e:
                print(f"  {name:20s} ERROR: {e}")
                ok = False
                continue
            if actual == expected:
                print(f"  {name:20s} OK")
            else:
                ok = False
                print(f"  {name:20s} MISMATCH\n    python={expected!r}\n    rust  ={actual!r}")

            try:
                root_path, dependencies = compile_files_to_artifacts(
                    main_path, module_dir / "artifacts"
                )
                native = rust_stdout(rust_bin, root_path, dependencies)
            except (RuntimeError, SystemExit) as e:
                print(f"  {name:20s} native ERROR: {e}")
                ok = False
                continue
            if native == expected:
                print(f"  {name:20s} native OK")
            else:
                ok = False
                print(
                    f"  {name:20s} native MISMATCH\n    python={expected!r}\n    rust  ={native!r}"
                )
    return ok


def rust_result(
    rust_bin: Path, obc: Path, extra: list[str] | None = None
) -> subprocess.CompletedProcess:
    """Run the Rust VM and keep stdout/stderr/exit code for assertions."""

    return subprocess.run(
        [str(rust_bin), *(extra or []), str(obc)],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )


def python_error(source: str, *, typed: bool):
    """Run a program that is expected to fail; return the Oort exception."""

    interpreter = ASTInterpreter(CompilerErrorHandler())
    if typed:
        program = compile_typed_module(lower_typed_module(build_ast(source)))
        vm = TypedCodeVM(interpreter)
    else:
        program = compile_module(lower_module(build_ast(source)))
        vm = BytecodeVM(interpreter)
    try:
        with contextlib.redirect_stdout(io.StringIO()), interpreter.runtime.activate():
            vm.run(program)
    except OortRuntimeError as exc:
        return exc
    return None


def error_differential(rust_bin: Path) -> bool:
    print("\n== error path (both VMs fail; innermost frame agrees on line) ==")
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        cases = [
            ("dynamic", DYNAMIC_ERROR_PROGRAMS, compile_to_obc, False),
            ("typed", TYPED_ERROR_PROGRAMS, compile_to_linked_bundle, True),
        ]
        for _label, programs, compile_fn, typed in cases:
            for name, (source, _proto, line) in programs.items():
                obc = Path(tmp) / f"{name}.obc"
                compile_fn(source, obc)
                py_error = python_error(source, typed=typed)
                proc = rust_result(rust_bin, obc)
                problems: list[str] = []
                if py_error is None:
                    problems.append("python did not raise")
                elif py_error.position.start_line != line:
                    problems.append(f"python line {py_error.position.start_line} != {line}")
                if proc.returncode != 1:
                    problems.append(f"rust exit {proc.returncode}")
                header = next(
                    (
                        text.strip()
                        for text in proc.stderr.splitlines()
                        if ": error: " in text or text.startswith("error: ")
                    ),
                    None,
                )
                if header is None:
                    problems.append("rust error has no standard header")
                elif f":{line}:" not in header and not header.startswith(f"{line}:"):
                    problems.append(f"line {line} missing in header {header!r}")
                if "note: called from " not in proc.stderr:
                    problems.append("rust error has no caller frame")
                if problems:
                    ok = False
                    print(f"  {name:20s} FAIL ({'; '.join(problems)})")
                    print(f"    rust stderr={proc.stderr.strip()!r}")
                else:
                    print(f"  {name:20s} OK")
    return ok


def trace_check(rust_bin: Path) -> bool:
    print("\n== trace (Rust --trace; instruction lines on stderr) ==")
    source = "#lang oort-core\n\ndef add(a: Int, b: Int) -> Int { a + b }\n\nprint(add(2, 3))\n"
    with tempfile.TemporaryDirectory() as tmp:
        obc = Path(tmp) / "trace.obc"
        compile_to_linked_bundle(source, obc)
        traced = rust_result(rust_bin, obc, extra=["--trace"])
        plain = rust_result(rust_bin, obc)
        problems: list[str] = []
        if traced.returncode != 0:
            problems.append(f"exit {traced.returncode}")
        if traced.stdout != "5\n":
            problems.append(f"stdout {traced.stdout!r}")
        for needle in ("[<main>]", "ADD_I", "-> R"):
            if needle not in traced.stderr:
                problems.append(f"missing {needle!r}")
        if "[<main>]" in plain.stderr:
            problems.append("trace leaked without --trace")
        if problems:
            print(f"  trace            FAIL ({'; '.join(problems)})")
            return False
        print("  trace            OK")
        return True


def disasm_check(rust_bin: Path) -> bool:
    print("\n== disassembly (Rust --disasm) ==")
    cases = [
        (
            "dynamic",
            "def add(a, b) { a + b }\nprint(add(2, 3))\n",
            compile_to_obc,
            ["Proto <main>", "ADD", "CALL"],
        ),
        (
            "typed",
            ("#lang oort-core\n\ndef add(a: Int, b: Int) -> Int { a + b }\n\nprint(add(2, 3))\n"),
            compile_to_linked_bundle,
            ["<main>() -> Unit", "ADD_I", "CALL"],
        ),
    ]
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for name, source, compile_fn, needles in cases:
            obc = Path(tmp) / f"{name}-disasm.obc"
            compile_fn(source, obc)
            proc = rust_result(rust_bin, obc, extra=["--disasm"])
            problems: list[str] = []
            if proc.returncode != 0:
                problems.append(f"exit {proc.returncode}")
            if proc.stderr.strip():
                problems.append(f"stderr {proc.stderr.strip()!r}")
            for needle in needles:
                if needle not in proc.stdout:
                    problems.append(f"missing {needle!r}")
            if proc.stdout.strip() == "5":
                problems.append("program was executed")
            if problems:
                ok = False
                print(f"  {name:16s} FAIL ({'; '.join(problems)})")
            else:
                print(f"  {name:16s} OK")
    return ok


def benchmark(rust_bin: Path, repeat: int) -> None:
    print(f"\n== benchmark (Rust VM, median of {repeat}, program-internal ms/rep) ==")
    with tempfile.TemporaryDirectory() as tmp:
        for name, src_path in BENCH_PROGRAMS.items():
            obc = Path(tmp) / f"{name}.obc"
            compile_to_obc(src_path.read_text(encoding="utf-8"), obc)
            timings = []
            result = None
            for _ in range(repeat):
                out = rust_stdout(rust_bin, obc)
                lines = out.strip().splitlines()
                result = lines[-2]
                timings.append(float(lines[-1]))
            med = statistics.median(timings)
            baseline = PYTHON_VM_BASELINE[name]
            speedup = baseline / med
            status = "OK" if result == BENCH_EXPECTED[name] else f"BAD result {result}"
            print(
                f"  {name:8s} {med:8.3f} ms  (python vm {baseline:7.1f} ms, "
                f"{speedup:5.1f}x faster)  [{status}]"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rust-bin", default=str(DEFAULT_RUST_BIN))
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--diff-only", action="store_true")
    parser.add_argument("--bench-only", action="store_true")
    options = parser.parse_args()
    rust_bin = Path(options.rust_bin)
    if not rust_bin.exists():
        print(f"rust binary not found: {rust_bin}", file=sys.stderr)
        return 2
    ok = True
    if not options.bench_only:
        ok = differential(rust_bin)
        ok = typed_differential(rust_bin) and ok
        ok = error_differential(rust_bin) and ok
        ok = trace_check(rust_bin) and ok
        ok = disasm_check(rust_bin) and ok
    if not options.diff_only:
        benchmark(rust_bin, options.repeat)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
