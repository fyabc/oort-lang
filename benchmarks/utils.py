#! /usr/bin/env python

from oort_lang.driver.arguments import get_main_parser, parse_main_args
from oort_lang.driver.compiler import Compiler


def get_compiler(argv: str) -> Compiler:
    parser = get_main_parser()
    args = parse_main_args(parser, argv)
    return Compiler(args)
