#! /usr/bin/env python

"""Measure the typed path (M2-M4) for the RESULTS research snapshot.

Runs the same scalar ``oort-core`` workloads on:

- the existing kind=0 bytecode VM (baseline),
- the typed HIR interpreter (M2),
- the typed bytecode VM (M3, Python),
- the Rust typed-bytecode VM (M4, kind=1).

Python runtimes are measured in-process around execution (compile excluded).
The Rust runtime is a subprocess; its startup is measured with an empty typed
program and subtracted to approximate exec time.

Usage:
    uv run --frozen python benchmarks/typed_run.py --repeat 5 --json > typed.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oort_lang.bytecode import TypedCodeVM, compile_module, compile_typed_module, write_typed_obc
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.hir import lower_module, lower_typed_module
from oort_lang.hir.typed_exec import TypedInterpreter
from oort_lang.runtime.bytecode_vm import BytecodeVM
from oort_lang.runtime.interpreter import ASTInterpreter
from tests.helpers import build_ast

PROGRAMS = {
    "fib20": """#lang oort-core

def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}

fib(20)
""",
    "loop20000": """#lang oort-core

def loop(n: Int) -> Int {
    var total: Int = 0
    var i: Int = 0
    while i < n {
        total = total + i
        i = i + 1
    }
    total
}

loop(20000)
""",
}

EMPTY = "#lang oort-core\n0\n"
DEFAULT_RUST_BIN = ROOT / "rust" / "target" / "release" / "oort-vm.exe"


def _git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _median_ms(function, repeat: int) -> float:
    function()
    timings = []
    for _ in range(repeat):
        started = time.perf_counter()
        function()
        timings.append((time.perf_counter() - started) * 1000)
    return statistics.median(timings)


def _python_runtimes(source: str, repeat: int) -> dict[str, float]:
    ast = build_ast(source)
    erased = compile_module(lower_module(ast))
    typed = lower_typed_module(ast)
    typed_code = compile_typed_module(typed)

    vm = BytecodeVM(ASTInterpreter(CompilerErrorHandler()))
    hir = TypedInterpreter(ASTInterpreter(CompilerErrorHandler()))
    tvm = TypedCodeVM(ASTInterpreter(CompilerErrorHandler()))

    return {
        "vm": _median_ms(lambda: vm.run(erased), repeat),
        "typed-hir": _median_ms(lambda: hir.run(typed), repeat),
        "typed-bc": _median_ms(lambda: tvm.run(typed_code), repeat),
    }


def _run_rust(rust_bin: Path, obc: Path) -> None:
    proc = subprocess.run(
        [str(rust_bin), str(obc)],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())


def _rust_runtime(source: str, rust_bin: Path, tmp: Path, repeat: int) -> dict[str, float]:
    obc = tmp / "program.obc"
    write_typed_obc(compile_typed_module(lower_typed_module(build_ast(source))), obc)
    wall = _median_ms(lambda: _run_rust(rust_bin, obc), repeat)

    empty_obc = tmp / "empty.obc"
    empty = lower_typed_module(build_ast(EMPTY))
    write_typed_obc(compile_typed_module(empty), empty_obc)
    startup = _median_ms(lambda: _run_rust(rust_bin, empty_obc), repeat)
    return {"wall_ms": wall, "startup_ms": startup, "exec_ms": max(wall - startup, 0.001)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--rust-bin", type=Path, default=DEFAULT_RUST_BIN)
    parser.add_argument("--json", action="store_true", help="Write compact JSON.")
    args = parser.parse_args()

    rust_bin: Path | None = args.rust_bin if args.rust_bin.exists() else None
    if rust_bin is None:
        print(f"warning: rust binary not found: {args.rust_bin}", file=sys.stderr)

    exec_ms: dict[str, dict[str, float]] = {}
    rust: dict[str, object] = {"wall_ms": {}, "exec_ms": {}, "startup_ms": None}
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        for workload, source in PROGRAMS.items():
            for name, value in _python_runtimes(source, args.repeat).items():
                exec_ms.setdefault(name, {})[workload] = value
            if rust_bin is not None:
                measured = _rust_runtime(source, rust_bin, tmp, args.repeat)
                exec_ms.setdefault("rust-typed", {})[workload] = measured["exec_ms"]
                wall = rust["wall_ms"]
                execs = rust["exec_ms"]
                assert isinstance(wall, dict) and isinstance(execs, dict)
                wall[workload] = measured["wall_ms"]
                execs[workload] = measured["exec_ms"]
                rust["startup_ms"] = measured["startup_ms"]

    result = {
        "date": date.today().isoformat(),
        "commit": _git_commit(),
        "repeat": args.repeat,
        "workloads": list(PROGRAMS),
        "exec_ms": exec_ms,
        "rust": rust,
        "notes": "typed scalar subset; Python in-process, Rust wall minus empty-program startup",
    }
    print(json.dumps(result, ensure_ascii=False, indent=None if args.json else 2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
