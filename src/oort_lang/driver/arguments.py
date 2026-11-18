#! /usr/bin/env python

import argparse

from .. import __version__

COMPILER_MODE_HELPS = {
    "ast": "Print AST.",
    "astm": "Print AST with metadata.",
    "eval": "Evaluate the AST (default).",
}


def get_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Oort compiler.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", nargs="?", help="Input filename")
    parser.add_argument("--version", action="version", version=f"Oort {__version__}")
    parser.add_argument(
        "-l",
        "--logging-level",
        type=str,
        default="WARNING",
        help="Logging level, default to %(default)r",
    )

    _help_strs = ["Output target format, default to %(default)r"]
    for mode, help_str in COMPILER_MODE_HELPS.items():
        _help_strs.append(f"- {mode}: {help_str}")
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        default="eval",
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

    return parser


def parse_main_args(parser: argparse.ArgumentParser, argv: str | None = None) -> argparse.Namespace:
    args = parser.parse_args(None if argv is None else argv.split())
    args.logging_level = args.logging_level.upper()

    if args.cmd is not None and args.input_file is not None:
        raise ValueError("Cannot specify both input file and command.")

    return args
