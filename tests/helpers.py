#! /usr/bin/env python

"""Shared helpers for the test suite."""

from pathlib import Path

from oort_lang.support.arguments import get_main_parser, parse_main_args
from oort_lang.top_level.compiler import Compiler

TEST_ASSETS_DIR = Path(__file__).parent / "assets"
REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"


def get_compiler(argv: str) -> Compiler:
    """Build a compiler from command-line style arguments."""
    parser = get_main_parser()
    args = parse_main_args(parser, argv)
    return Compiler(args)
