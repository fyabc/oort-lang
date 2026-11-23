#! /usr/bin/env python

import argparse
import os
from collections.abc import Sequence

from .. import __version__


def _parse_size(text: str) -> int:
    """Parse a byte size with an optional K/M/G suffix."""

    value = text.strip().upper()
    scale = 1
    if value.endswith(("K", "M", "G")):
        scale = {"K": 1024, "M": 1024**2, "G": 1024**3}[value[-1]]
        value = value[:-1]
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid size: {text!r}") from exc
    if number < 0:
        raise argparse.ArgumentTypeError(f"size must be non-negative: {text!r}")
    return number * scale


def resolve_cache_dir(args: argparse.Namespace) -> str | None:
    """Resolve the cache directory from flags and the environment."""

    if getattr(args, "no_cache", False):
        return None
    return getattr(args, "cache_dir", None) or os.environ.get("OORT_CACHE_DIR") or None


COMPILER_MODE_HELPS = {
    "ast": "Print AST.",
    "astm": "Print AST with metadata.",
    "hir": "Lower to HIR and print it.",
    "thir": "Lower to typed HIR and print it (research; restricted core subset).",
    "tbc": "Compile typed HIR to typed bytecode and print disassembly (research).",
    "bc": "Compile to bytecode and print disassembly.",
    "tvm": "Execute the typed HIR subset (research).",
    "vm": "Execute the supported bytecode subset (default).",
    "eval": "Evaluate the AST (tree-walking interpreter, fallback).",
}


def get_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Oort compiler.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", nargs="?", help="Input filename")
    parser.add_argument(
        "script_args",
        nargs="*",
        metavar="ARG",
        help="Arguments passed to the Oort program (os.args)",
    )
    parser.add_argument("--version", action="version", version=f"Oort {__version__}")
    parser.add_argument(
        "-l",
        "--logging-level",
        type=str,
        default="WARNING",
        help="Logging level, default to %(default)r",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help=(
            "Plain diagnostic output: no rich console, one line per record.\n"
            "Useful when piping output or when wrapping hides the message."
        ),
    )

    _help_strs = ["Output target format, default to %(default)r"]
    for mode, help_str in COMPILER_MODE_HELPS.items():
        _help_strs.append(f"- {mode}: {help_str}")
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        default="vm",
        choices=list(COMPILER_MODE_HELPS),
        help="\n".join(_help_strs),
    )
    parser.add_argument(
        "-c",
        "--cmd",
        type=str,
        default=None,
        help="Program passed in as string",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        metavar="DIR",
        help=(
            "Enable the typed artifact cache in DIR.\n"
            "Entries are keyed by source, module id, compiler, ABI versions\n"
            "and direct dependency interface hashes."
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable the typed artifact cache, overriding --cache-dir and OORT_CACHE_DIR.",
    )
    parser.add_argument(
        "--cache-max-size",
        type=_parse_size,
        default=None,
        metavar="SIZE",
        help=(
            "Evict least-recently-used cache entries above SIZE bytes.\n"
            "Accepts K/M/G suffixes (e.g. 128M)."
        ),
    )
    parser.add_argument(
        "--cache-clean",
        action="store_true",
        help="Remove cached typed artifacts for the current schema version (requires --cache-dir).",
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Print typed artifact cache entries and size to stderr (requires --cache-dir).",
    )
    parser.add_argument(
        "-I",
        "--module-path",
        action="append",
        default=[],
        metavar="DIR",
        help=(
            "Add DIR to the module search path (repeatable).\n"
            "Unlike Python's -I, this does not enable isolated mode."
        ),
    )

    return parser


def parse_main_args(
    parser: argparse.ArgumentParser, argv: str | Sequence[str] | None = None
) -> argparse.Namespace:
    if argv is None:
        arg_list = None
    elif isinstance(argv, str):
        arg_list = argv.split()
    else:
        arg_list = list(argv)
    args = parser.parse_args(arg_list)
    args.logging_level = args.logging_level.upper()

    if args.cmd is not None and args.input_file is not None:
        # argparse cannot distinguish `-c CODE ARG...`: a positional after
        # `-c` lands in `input_file`. Treat it (and the rest) as program args.
        args.script_args.insert(0, args.input_file)
        args.input_file = None

    return args
