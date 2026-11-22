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

from oort_lang.bytecode import compile_module, compile_typed_module, write_typed_obc
from oort_lang.bytecode.serialize import write_obc
from oort_lang.bytecode.typed_vm import TypedCodeVM
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.hir import lower_module, lower_typed_module
from oort_lang.runtime.bytecode_vm import BytecodeVM
from oort_lang.runtime.interpreter import ASTInterpreter
from tests.helpers import build_ast

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


def rust_stdout(rust_bin: Path, obc: Path) -> str:
    proc = subprocess.run(
        [str(rust_bin), str(obc)],
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
    print("\n== typed differential (kind=1 Rust VM vs Python typed VM, stdout) ==")
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for name, source in TYPED_DIFF_PROGRAMS.items():
            obc = Path(tmp) / f"{name}.obc"
            compile_to_typed_obc(source, obc)
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
    if not options.diff_only:
        benchmark(rust_bin, options.repeat)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
