#! /usr/bin/env python

"""Diagnostic benchmark: typed artifact cache cold vs warm (OP 0030).

Measures end-to-end ``-t tvm`` runs for typed examples and a generated
many-module program with an empty cache versus a populated one. Parsing and
type checking still run on every invocation, so the speedup reflects only
lowering, typed bytecode and the linker's cache hits. The ``builds`` columns
show the direct effect: how many module artifacts were compiled.

This is a research diagnostic, not a CI gate.

Usage:
    uv run --frozen python benchmarks/cache_run.py --repeat 5
    uv run --frozen python benchmarks/cache_run.py --repeat 5 --modules 48
    uv run --frozen python benchmarks/cache_run.py --repeat 5 --json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import oort_lang.bytecode.typed_artifact as artifact_module
from tests.helpers import EXAMPLES_DIR, get_compiler

WORKLOADS = {
    "typed_subset": EXAMPLES_DIR / "08_core" / "08_15_typed_subset.ort",
    "typed_adts": EXAMPLES_DIR / "08_core" / "08_18_typed_adts.ort",
    "typed_modules": EXAMPLES_DIR / "08_core" / "08_20_typed_modules.ort",
}

_REAL_BUILD = artifact_module.build_typed_artifact
_BUILDS = [0]


def _counting_build(unit, origins=None):
    _BUILDS[0] += 1
    return _REAL_BUILD(unit, origins)


artifact_module.build_typed_artifact = _counting_build


def run_once(main: Path, cache_dir: Path) -> tuple[float, str, int]:
    compiler = get_compiler(["NOT_EXIST", "-t", "tvm", "--cache-dir", str(cache_dir)])
    buffer = io.StringIO()
    _BUILDS[0] = 0
    start = time.perf_counter()
    with contextlib.redirect_stdout(buffer):
        compiler.run_file(main)
    elapsed = (time.perf_counter() - start) * 1000.0
    return elapsed, buffer.getvalue(), _BUILDS[0]


def make_many_modules(root: Path, count: int) -> tuple[Path, int]:
    """Generate ``count`` independent libraries plus one importer."""

    root.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        (root / f"lib_{index:02d}.ort").write_text(
            f"""#lang oort-core
enum Item_{index} {{ A_{index}(value: Int), B_{index} }}
def value_{index}(x: Int) -> Int {{
    match A_{index}(x) {{ A_{index}(value) => value, B_{index} => {index} }}
}}
""",
            encoding="utf-8",
        )
    imports = "".join(f'from "./lib_{index:02d}" import value_{index}\n' for index in range(count))
    body = "".join(f"    total = total + value_{index}({index + 1})\n" for index in range(count))
    main = root / "main.ort"
    main.write_text(
        f"""#lang oort-core
{imports}def total() -> Int {{
    var total: Int = 0
{body}    total
}}

print(total())
""",
        encoding="utf-8",
    )
    return main, count + 1


def measure_workload(
    name: str,
    main: Path,
    repeat: int,
    root: Path,
    modules: int | None = None,
) -> dict[str, object]:
    cold_cache = root / f"{name}-cold"
    cold_ms, expected, cold_builds = run_once(main, cold_cache)

    warm_cache = root / f"{name}-warm"
    _, warm_output, _ = run_once(main, warm_cache)
    if warm_output != expected:
        raise RuntimeError(f"{name}: warm output differs from cold output")
    warm_samples: list[float] = []
    warm_builds = 0
    for _ in range(max(repeat, 1)):
        elapsed, output, builds = run_once(main, warm_cache)
        if output != expected:
            raise RuntimeError(f"{name}: warm output differs from cold output")
        warm_samples.append(elapsed)
        warm_builds += builds
    warm_ms = statistics.median(warm_samples)
    return {
        "workload": name,
        "modules": modules,
        "cold_builds": cold_builds,
        "warm_builds": warm_builds,
        "cold_ms": round(cold_ms, 3),
        "warm_ms": round(warm_ms, 3),
        "speedup": round(cold_ms / warm_ms, 2) if warm_ms else None,
    }


def measure(repeat: int, module_count: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run_once(WORKLOADS["typed_subset"], root / "warmup")

        for name, main in WORKLOADS.items():
            results.append(measure_workload(name, main, repeat, root))
        many_main, modules = make_many_modules(root / "many", module_count)
        results.append(
            measure_workload(f"many_modules_{module_count}", many_main, repeat, root, modules)
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=5, help="warm samples per workload")
    parser.add_argument(
        "--modules", type=int, default=32, help="module count for the generated workload"
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    results = measure(args.repeat, args.modules)
    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print(f"typed artifact cache (warm median of {args.repeat}; builds summed over samples)")
    print(
        f"{'workload':18s} {'mods':>5s} {'cold#':>6s} {'warm#':>6s} "
        f"{'cold ms':>10s} {'warm ms':>10s} {'speedup':>8s}"
    )
    for row in results:
        modules = "-" if row["modules"] is None else str(row["modules"])
        print(
            f"{row['workload']:18s} {modules:>5s} {row['cold_builds']:>6d} "
            f"{row['warm_builds']:>6d} {row['cold_ms']:10.3f} {row['warm_ms']:10.3f} "
            f"{row['speedup']!s:>8s}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
