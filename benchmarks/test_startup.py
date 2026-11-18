#! /usr/bin/env python

"""Startup benchmarks: compiler construction and an empty program."""

from benchmarks.bench_utils import compile_and_run, get_compiler
from oort_lang.runtime import Runtime


def test_compiler_construction(benchmark):
    benchmark(get_compiler)


def test_empty_program(benchmark):
    benchmark(compile_and_run, "")


def test_runtime_construction(benchmark):
    benchmark(Runtime)
