#! /usr/bin/env python

"""Reference-suite wrapper for the Rust VM spike.

The cross-language runner (run.py) hands each runtime a source program path.
The Rust VM consumes compiled ``.obc`` bytecode, so this wrapper compiles the
``.ort`` source to ``.obc`` (cached by mtime) and then executes the Rust VM,
forwarding stdout/stderr/exit code. Caching means repeated runs (and the startup
measurement) reflect the Rust VM executing precompiled bytecode, not the Python
compile step.

The Rust binary is located via ``OORT_RUST_BIN`` or the default release/debug
build under ``rust/target``.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CACHE_DIR = Path(__file__).resolve().parent / ".obc-cache"


def _rust_bin() -> Path:
    override = os.environ.get("OORT_RUST_BIN")
    if override:
        return Path(override)
    for profile in ("release", "debug"):
        candidate = ROOT / "rust" / "target" / profile / "oort-vm.exe"
        if candidate.exists():
            return candidate
    raise SystemExit("oort-vm binary not found; build rust/ or set OORT_RUST_BIN")


def _compile_cached(source: Path) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    obc = CACHE_DIR / (source.stem + ".obc")
    if not obc.exists() or obc.stat().st_mtime < source.stat().st_mtime:
        # Import the (heavy) frontend only when actually compiling, so cached
        # runs stay fast and the startup measurement reflects the Rust VM.
        from oort_lang.bytecode import compile_module
        from oort_lang.bytecode.serialize import write_obc
        from oort_lang.hir import lower_module
        from tests.helpers import build_ast

        program = compile_module(lower_module(build_ast(source.read_text(encoding="utf-8"))))
        write_obc(program, obc)
    return obc


def main() -> int:
    args = sys.argv[1:]
    if args == ["--version"]:
        print("oort-rust spike (register VM consuming .obc)")
        return 0
    if len(args) != 1:
        print("usage: oort_rust.py <program.ort>", file=sys.stderr)
        return 2
    source = Path(args[0])
    obc = _compile_cached(source)
    proc = subprocess.run([str(_rust_bin()), str(obc)], check=False)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
