#! /usr/bin/env python

"""Diagnostic benchmark: typed artifact cache cold vs warm (OP 0030).

Measures end-to-end ``-t tvm`` runs for a few typed examples with an empty
cache versus a populated one. Parsing and type checking still run on every
invocation, so the speedup reflects only lowering, typed bytecode and the
linker's cache hits.

This is a research diagnostic, not a CI gate.

Usage:
    uv run --frozen python benchmarks/cache_run.py --repeat 5
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

from tests.helpers import EXAMPLES_DIR, get_compiler

WORKLOADS = {
    "typed_subset": EXAMPLES_DIR / "08_core" / "08_15_typed_subset.ort",
    "typed_adts": EXAMPLES_DIR / "08_core" / "08_18_typed_adts.ort",
    "typed_modules": EXAMPLES_DIR / "08_core" / "08_20_typed_modules.ort",
}


def run_once(main: Path, cache_dir: Path) -> tuple[float, str]:
    compiler = get_compiler(["NOT_EXIST", "-t", "tvm", "--cache-dir", str(cache_dir)])
    buffer = io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(buffer):
        compiler.run_file(main)
    elapsed = (time.perf_counter() - start) * 1000.0
    return elapsed, buffer.getvalue()


def measure(repeat: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory() as tmp:
        warmup_cache = Path(tmp) / "warmup"
        run_once(WORKLOADS["typed_subset"], warmup_cache)

        for name, main in WORKLOADS.items():
            cold_cache = Path(tmp) / f"{name}-cold"
            cold_ms, expected = run_once(main, cold_cache)
            warm_cache = Path(tmp) / f"{name}-warm"
            _, warm_output = run_once(main, warm_cache)
            if warm_output != expected:
                raise RuntimeError(f"{name}: warm output differs from cold output")
            warm_samples: list[float] = []
            for _ in range(max(repeat, 1)):
                elapsed, output = run_once(main, warm_cache)
                if output != expected:
                    raise RuntimeError(f"{name}: warm output differs from cold output")
                warm_samples.append(elapsed)
            warm_ms = statistics.median(warm_samples)
            results.append(
                {
                    "workload": name,
                    "cold_ms": round(cold_ms, 3),
                    "warm_ms": round(warm_ms, 3),
                    "speedup": round(cold_ms / warm_ms, 2) if warm_ms else None,
                }
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=5, help="warm samples per workload")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    results = measure(args.repeat)
    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print(f"typed artifact cache (warm median of {args.repeat})")
    print(f"{'workload':16s} {'cold ms':>10s} {'warm ms':>10s} {'speedup':>8s}")
    for row in results:
        print(
            f"{row['workload']:16s} {row['cold_ms']:10.3f} {row['warm_ms']:10.3f} "
            f"{row['speedup']!s:>8s}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
