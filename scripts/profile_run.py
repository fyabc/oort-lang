#! /usr/bin/env python

"""Profile an Oort program under a chosen backend.

cProfile-based hot-function report plus optional wall-clock repeats, for the
"where did the time go" questions that precede optimization work. For sampling
profiles (py-spy) and benchmark methodology see benchmarks/README.md.

Usage:

    uv run --frozen python scripts/profile_run.py -c 'fib(18)' -t vm
    uv run --frozen python scripts/profile_run.py examples/05_stdlib/05_00_collections.ort --repeat 5
    uv run --frozen python scripts/profile_run.py -c 'run()' --top 30 --all
"""

import argparse
import cProfile
import io
import pstats
import statistics
import sys
import time
from pathlib import Path

from oort_lang.driver.arguments import get_main_parser, parse_main_args
from oort_lang.driver.compiler import Compiler


def build_compiler(target: str) -> Compiler:
    args = parse_main_args(get_main_parser(), ["NOT_EXIST", "-t", target])
    return Compiler(args)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", nargs="?", help="Oort source file (omit with -c)")
    parser.add_argument("-c", "--cmd", help="Oort source passed as a string")
    parser.add_argument(
        "-t", "--target", choices=("eval", "vm"), default="vm", help="Backend (default: vm)"
    )
    parser.add_argument("--top", type=int, default=20, help="Top functions to print")
    parser.add_argument(
        "--sort",
        choices=("tottime", "cumulative"),
        default="tottime",
        help="Sort key (default: tottime — hot leaves; cumulative shows the call tree)",
    )
    parser.add_argument("--all", action="store_true", help="Do not filter frames to oort_lang code")
    parser.add_argument(
        "--repeat",
        type=int,
        default=0,
        help="Also report the wall-clock median of N extra runs",
    )
    options = parser.parse_args()

    if bool(options.file) == bool(options.cmd):
        parser.error("exactly one of FILE or -c is required")

    def run_once() -> None:
        compiler = build_compiler(options.target)
        if options.file is not None:
            compiler.run_file(Path(options.file))
        else:
            compiler.run_string(options.cmd)

    profiler = cProfile.Profile()
    profiler.enable()
    run_once()
    profiler.disable()

    report = io.StringIO()
    stats = pstats.Stats(profiler, stream=report).sort_stats(options.sort)
    if options.all:
        stats.print_stats(options.top)
    else:
        stats.print_stats("oort_lang", options.top)
    print(report.getvalue(), end="")

    if options.repeat > 0:
        durations = []
        for _ in range(options.repeat):
            start = time.perf_counter()
            run_once()
            durations.append((time.perf_counter() - start) * 1000)
        print(f"\nwall clock over {options.repeat} run(s), ms:")
        print(f"  median {statistics.median(durations):8.2f}")
        print(f"  min    {min(durations):8.2f}")
        print(f"  max    {max(durations):8.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
