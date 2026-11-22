#! /usr/bin/env python

"""Diagnostic benchmark: static core library vs dynamic object library.

This is a manual research benchmark, not a CI gate. It compares four paths:

- ``dynamic``: one ``oort-object`` program containing the library and driver,
  executed by the Python VM;
- ``core-python``: the equivalent ``oort-core`` program (typed bytecode),
  executed by the Python typed VM;
- ``core-rust``: the same typed bytecode, executed by the Rust typed VM;
- ``b1``: an ``oort-object`` driver importing the core library through the B1
  boundary (Python typed VM + guards + copy-on-boundary).

Python variants are measured in-process (compile + execute, no process startup);
the Rust variant uses subprocess wall time minus an empty typed-program startup.
B1 additionally pays container copies at the boundary; the ``identity`` workload
isolates that cost.

Usage:
    uv run --frozen python benchmarks/boundary_run.py --repeat 3
    uv run --frozen python benchmarks/boundary_run.py --json
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import io
import json
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oort_lang.bytecode import compile_typed_module, write_typed_obc
from oort_lang.hir import lower_typed_module
from tests.helpers import build_ast, get_compiler

DEFAULT_RUST_BIN = ROOT / "rust" / "target" / "release" / "oort-vm.exe"


@dataclasses.dataclass(frozen=True)
class Workload:
    name: str
    expected: str
    imports: tuple[str, ...]
    core_lib: str
    dynamic_lib: str
    object_driver: str
    core_driver: str


def _list_literal(count: int) -> str:
    return "[" + ", ".join(str(index) for index in range(count)) + "]"


def _dict_literal(count: int) -> str:
    items = ", ".join(f'"k{index}": {index}' for index in range(count))
    return "{: " + items + " :}"


def _set_literal(count: int) -> str:
    return "{. " + ", ".join(str(index) for index in range(count)) + " .}"


def _workloads() -> list[Workload]:
    return [
        Workload(
            name="calls",
            expected="20000",
            imports=("add",),
            core_lib="def add(a: Int, b: Int) -> Int { a + b }\n",
            dynamic_lib="def add(a, b) { a + b }\n",
            object_driver="""\
def run() {
    var total = 0
    var i = 0
    while i < 20000 {
        total = add(total, 1)
        i = i + 1
    }
    total
}

print(run())
""",
            core_driver="""\
def run() -> Int {
    var total: Int = 0
    var i: Int = 0
    while i < 20000 {
        total = add(total, 1)
        i = i + 1
    }
    total
}

print(run())
""",
        ),
        Workload(
            name="fib20",
            expected="6765",
            imports=("fib",),
            core_lib="""\
def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}
""",
            dynamic_lib="""\
def fib(n) {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}
""",
            object_driver="print(fib(20))\n",
            core_driver="print(fib(20))\n",
        ),
        Workload(
            name="list-sum-100",
            expected=str(sum(range(100))),
            imports=("total",),
            core_lib="""\
def total(values: List[Int]) -> Int {
    var sum: Int = 0
    for value in values { sum = sum + value }
    sum
}
""",
            dynamic_lib="""\
def total(values) {
    var sum = 0
    for value in values { sum = sum + value }
    sum
}
""",
            object_driver=f"print(total({_list_literal(100)}))\n",
            core_driver=f"print(total({_list_literal(100)}))\n",
        ),
        Workload(
            name="identity-100x500",
            expected="50000",
            imports=("identity",),
            core_lib="""\
def identity(values: List[Int]) -> List[Int] { values }
""",
            dynamic_lib="""\
def identity(values) { values }
""",
            object_driver=f"""\
def run() {{
    val values = {_list_literal(100)}
    var total = 0
    var i = 0
    while i < 500 {{
        total = total + len(identity(values))
        i = i + 1
    }}
    total
}}

print(run())
""",
            core_driver=f"""\
def run() -> Int {{
    var values: List[Int] = {_list_literal(100)}
    var total: Int = 0
    var i: Int = 0
    while i < 500 {{
        total = total + len(identity(values))
        i = i + 1
    }}
    total
}}

print(run())
""",
        ),
        Workload(
            name="dict-lookup-32x1000",
            expected=str(31 * 1000),
            imports=("score",),
            core_lib="""\
def score(scores: Dict[String, Int], key: String) -> Int { scores[key] }
""",
            dynamic_lib="""\
def score(scores, key) { scores[key] }
""",
            object_driver=f"""\
def run() {{
    val scores = {_dict_literal(32)}
    var total = 0
    var i = 0
    while i < 1000 {{
        total = total + score(scores, "k31")
        i = i + 1
    }}
    total
}}

print(run())
""",
            core_driver=f"""\
def run() -> Int {{
    var scores: Dict[String, Int] = {_dict_literal(32)}
    var total: Int = 0
    var i: Int = 0
    while i < 1000 {{
        total = total + score(scores, "k31")
        i = i + 1
    }}
    total
}}

print(run())
""",
        ),
        Workload(
            name="set-count-32x1000",
            expected=str(32 * 1000),
            imports=("count",),
            core_lib="""\
def count(values: Set[Int]) -> Int { len(values) }
""",
            dynamic_lib="""\
def count(values) { len(values) }
""",
            object_driver=f"""\
def run() {{
    val values = {_set_literal(32)}
    var total = 0
    var i = 0
    while i < 1000 {{
        total = total + count(values)
        i = i + 1
    }}
    total
}}

print(run())
""",
            core_driver=f"""\
def run() -> Int {{
    var values: Set[Int] = {_set_literal(32)}
    var total: Int = 0
    var i: Int = 0
    while i < 1000 {{
        total = total + count(values)
        i = i + 1
    }}
    total
}}

print(run())
""",
        ),
        Workload(
            name="concat-2000",
            expected="2000",
            imports=("pair",),
            core_lib="""\
def pair(a: String, b: String) -> String { a + b }
""",
            dynamic_lib="""\
def pair(a, b) { a + b }
""",
            object_driver="""\
def run() {
    var total = 0
    var i = 0
    while i < 2000 {
        if pair("a", "b") == "ab" {
            total = total + 1
        }
        i = i + 1
    }
    total
}

print(run())
""",
            core_driver="""\
def run() -> Int {
    var total: Int = 0
    var i: Int = 0
    while i < 2000 {
        if pair("a", "b") == "ab" {
            total = total + 1
        }
        i = i + 1
    }
    total
}

print(run())
""",
        ),
    ]


def _run(command: list[str], *, expected: str | None = None) -> float:
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    elapsed = (time.perf_counter() - started) * 1000
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(command)}\n{proc.stderr.strip()}"
        )
    if expected is not None and proc.stdout.strip() != expected:
        raise RuntimeError(
            f"unexpected output for {' '.join(command)}: {proc.stdout!r}, expected {expected!r}"
        )
    return elapsed


def _median_ms(command: list[str], repeat: int, *, expected: str | None = None) -> float:
    _run(command, expected=expected)
    return statistics.median(_run(command, expected=expected) for _ in range(repeat))


def _python_measure(
    path: Path,
    target: str,
    repeat: int,
    *,
    expected: str,
) -> float:
    """Median in-process compile+execution time; avoids process startup noise."""
    compiler = get_compiler(["NOT_EXIST", "-t", target])

    def invoke() -> str:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            compiler.run_file(path)
        return output.getvalue()

    first = invoke()
    if first.strip() != expected:
        raise RuntimeError(f"unexpected output for {path}: {first!r}, expected {expected!r}")
    samples = []
    for _ in range(repeat):
        started = time.perf_counter()
        invoke()
        samples.append((time.perf_counter() - started) * 1000)
    return statistics.median(samples)


def _compile_rust(source: str, path: Path) -> None:
    typed = lower_typed_module(build_ast(source))
    write_typed_obc(compile_typed_module(typed), path)


def _cell(name: str, value: float) -> str:
    if name == "core-rust" and value < 0.01:
        return f"{'<0.01':>11s}"
    return f"{value:11.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--rust-bin", type=Path, default=DEFAULT_RUST_BIN)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rust_bin = args.rust_bin if args.rust_bin.exists() else None
    if rust_bin is None:
        print(f"warning: rust binary not found: {args.rust_bin}", file=sys.stderr)

    rows: dict[str, dict[str, float]] = {}
    startup: dict[str, float] = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        if rust_bin is not None:
            empty_obc = tmp / "empty.obc"
            _compile_rust("#lang oort-core\n0\n", empty_obc)
            startup["core-rust"] = _median_ms([str(rust_bin), str(empty_obc)], args.repeat)

        for workload in _workloads():
            source_dir = tmp / workload.name
            source_dir.mkdir()
            core_source = f"#lang oort-core\n\n{workload.core_lib}\n{workload.core_driver}"
            dynamic_source = (
                f"#lang oort-object\n\n{workload.dynamic_lib}\n{workload.object_driver}"
            )
            core_program = source_dir / "core.ort"
            core_program.write_text(core_source, encoding="utf-8")
            dynamic_program = source_dir / "dynamic.ort"
            dynamic_program.write_text(dynamic_source, encoding="utf-8")

            core_lib = source_dir / "lib.ort"
            core_lib.write_text(f"#lang oort-core\n\n{workload.core_lib}", encoding="utf-8")
            imports = ", ".join(workload.imports)
            b1_program = source_dir / "b1.ort"
            b1_program.write_text(
                f'#lang oort-object\n\nfrom "./lib" import {imports}\n\n{workload.object_driver}',
                encoding="utf-8",
            )

            measurements: dict[str, float] = {}
            measurements["dynamic"] = _python_measure(
                dynamic_program,
                "vm",
                args.repeat,
                expected=workload.expected,
            )
            measurements["core-python"] = _python_measure(
                core_program,
                "tvm",
                args.repeat,
                expected=workload.expected,
            )
            measurements["b1"] = _python_measure(
                b1_program,
                "vm",
                args.repeat,
                expected=workload.expected,
            )
            if rust_bin is not None:
                obc = source_dir / "core.obc"
                _compile_rust(core_source, obc)
                measurements["core-rust"] = (
                    _median_ms(
                        [str(rust_bin), str(obc)],
                        args.repeat,
                        expected=workload.expected,
                    )
                    - startup["core-rust"]
                )
            rows[workload.name] = {name: max(value, 0.001) for name, value in measurements.items()}

    if args.json:
        print(
            json.dumps(
                {
                    "repeat": args.repeat,
                    "startup_ms": startup,
                    "workloads_ms": rows,
                    "notes": (
                        "Python in-process compile+exec; Rust wall minus empty startup; "
                        "b1 includes guards and copy-on-boundary"
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    columns = ["dynamic", "core-python", "core-rust", "b1"]
    if startup:
        print(
            "rust startup (ms):",
            ", ".join(f"{name}={value:.1f}" for name, value in startup.items()),
        )
        print()
    print(f"{'workload':22s} " + " ".join(f"{name:>11s}" for name in columns) + "  b1/dyn")
    for name, values in rows.items():
        cells = " ".join(
            _cell(name, values[name]) if name in values else f"{'-':>11s}" for name in columns
        )
        ratio = values["b1"] / values["dynamic"] if "dynamic" in values else float("nan")
        print(f"{name:22s} {cells}  {ratio:6.2f}x")
    print()
    print("Python: in-process compile+exec; Rust: wall minus empty startup.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
