# Benchmarks

The benchmark suite uses [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
and exercises the real compiler pipeline, not a stripped-down harness.

| File | Level | Covers |
|------|-------|--------|
| `test_micro.py` | micro | arithmetic, locals, calls, attributes, indexing, dicts |
| `test_macro.py` | macro | recursion, loops, method dispatch |
| `test_startup.py` | startup | compiler/runtime construction, empty program |
| `test_memory.py` | memory | peak allocation ceilings for a runtime and a program |
| `test_ast_interpreter.py` | macro | historical Fibonacci baseline |

## Running

```bash
uv run pytest benchmarks/ -q
uv run pytest benchmarks/ --benchmark-json=benchmark.json -q
```

`bench_utils.compile_program` parses, resolves and builds an interpreter once;
micro/macro tests then measure only `interpreter.run(ast)`. Startup tests
measure construction, and compile-time work is covered by startup/empty
program rather than mixed into every micro number.

## Regression tracking

`.github/workflows/benchmark.yml` runs on pushes to `main` and on manual
dispatch, writes `benchmark.json`, and stores results with
[github-action-benchmark](https://github.com/benchmark-action/github-action-benchmark).
An alert is raised at a 150% regression against the stored history. PRs do not
write history by default (forked PRs cannot push benchmark results).

For local comparisons, save a baseline on a quiet machine and compare:

```bash
uv run pytest benchmarks/ --benchmark-json=baseline.json -q
# after a change
uv run pytest benchmarks/ --benchmark-json=current.json \
  --benchmark-compare=baseline.json --benchmark-compare-fail=median:10% -q
```

## Profiling

Benchmarks tell us *that* something regressed; profilers tell us *where*.

```bash
# Sampling profile of the macro suite
uvx py-spy record -o profile.svg -- uv run pytest benchmarks/test_macro.py -q

# Line-level CPU + memory attribution
uvx scalene --cli --reduced-profile benchmarks/test_macro.py

# Allocation tracing for the memory suite
uvx memray run -o memory.bin -m pytest benchmarks/test_memory.py -q
uvx memray flamegraph memory.bin
```

Do not commit generated profiles or benchmark JSON files.
