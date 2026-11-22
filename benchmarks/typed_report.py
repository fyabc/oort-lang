#! /usr/bin/env python

"""Render the typed-path (M2-M4) snapshot section of ``benchmarks/RESULTS.md``.

The section lives between HTML markers so it can be refreshed without touching
the report.py-generated sections. Numbers come from ``benchmarks/typed_run.py``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- TYPED-BENCH-START -->"
END = "<!-- TYPED-BENCH-END -->"

LABELS = {
    "vm": ("Oort VM (kind=0)", "基线"),
    "typed-hir": ("Typed HIR 解释器 (M2)", "Python，in-process"),
    "typed-bc": ("Typed 字节码 VM (M3)", "Python，in-process"),
    "rust-typed": ("Rust typed VM (M4)", "kind=1，exec 扣启动"),
}


def _fmt(value: Any) -> str:
    return "-" if value is None else f"{float(value):.1f} ms"


def _ratio(exec_ms: dict[str, dict[str, float]], left: str, right: str) -> str:
    values = []
    for workload in ("fib20", "loop20000"):
        lhs = exec_ms.get(left, {}).get(workload)
        rhs = exec_ms.get(right, {}).get(workload)
        if isinstance(lhs, (int, float)) and isinstance(rhs, (int, float)) and rhs > 0:
            values.append(float(lhs) / float(rhs))
    if not values:
        return ""
    low, high = min(values), max(values)
    return f"{low:.2f}–{high:.2f}×"


def render(typed: dict[str, Any]) -> str:
    exec_ms = typed.get("exec_ms") or {}
    lines = [
        "## 6. 类型化路径（研究快照）",
        "",
        f"> 快照日期：{typed.get('date', '?')}；提交：`{typed.get('commit', 'unknown')}`；"
        f"重复 {typed.get('repeat', '?')} 次取中位数。",
        "> 仅标量子集（fib20 / loop 20000）；Python 运行时为进程内计时，Rust 为",
        "> 子进程 wall time 扣除空 typed 程序启动。该节不进入门禁，由",
        "> `benchmarks/typed_run.py` + `typed_report.py` 生成。",
        "",
        "| 运行时 | fib(20) | loop 20000 | 说明 |",
        "|---|---:|---:|---|",
    ]
    for runtime in ("vm", "typed-hir", "typed-bc", "rust-typed"):
        label, note = LABELS[runtime]
        values = exec_ms.get(runtime) or {}
        lines.append(
            f"| {label} | {_fmt(values.get('fib20'))} | {_fmt(values.get('loop20000'))} | {note} |"
        )
    lines.append("")
    typed_bc_ratio = _ratio(exec_ms, "typed-bc", "vm")
    rust_speedup = _ratio(exec_ms, "vm", "rust-typed")
    if typed_bc_ratio:
        lines.append(
            f"Python typed 字节码相对 kind=0 VM：**{typed_bc_ratio}**（仍更慢，"
            "类型断言与解码开销；M3 只验证 ABI）。"
        )
    if rust_speedup:
        lines.append(
            f"Rust typed 字节码比 kind=0 VM 快 **{rust_speedup}**（同 exec 口径；"
            "boxed 值仍是 spike 表示，M4 后续做未装箱）。"
        )
    lines.extend(
        [
            "",
            "生成命令：",
            "",
            "```bash",
            "uv run --frozen python benchmarks/typed_run.py --repeat 5 --json > typed.json",
            "uv run --frozen python benchmarks/typed_report.py --typed typed.json",
            "```",
        ]
    )
    return "\n".join(lines)


def inject(results_path: Path, section: str) -> None:
    text = results_path.read_text(encoding="utf-8")
    block = f"{START}\n{section}\n{END}"
    if START in text and END in text:
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        text = f"{before}{block}{after}"
    else:
        text = f"{text.rstrip()}\n\n{block}\n"
    results_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--typed", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "RESULTS.md")
    args = parser.parse_args()
    typed = json.loads(args.typed.read_text(encoding="utf-8"))
    inject(args.output, render(typed))
    print(f"updated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
