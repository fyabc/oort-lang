#! /usr/bin/env python

"""Round-trip and execution tests for the ``.obc`` bytecode serialization."""

import contextlib
import io

import pytest

from oort_lang.bytecode import compile_module
from oort_lang.bytecode.serialize import ObcError, read_obc, write_obc
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.hir import lower_module
from oort_lang.runtime.bytecode_vm import BytecodeVM
from oort_lang.runtime.interpreter import ASTInterpreter
from tests.helpers import build_ast

_PROGRAMS = [
    "print(1 + 2 * 3)\n",
    "def fib(n) { if n <= 1: return n\nfib(n - 1) + fib(n - 2) }\nprint(fib(10))\n",
    "var total = 0\nfor i in range(100) { total = total + i }\nprint(total)\n",
    (
        "class Counter {\n"
        "    def __init__() { this.value = 0 }\n"
        "    def bump() { this.value = this.value + 1 }\n"
        "}\n"
        "val c = Counter()\nc.bump()\nc.bump()\nprint(c.value)\n"
    ),
    (
        "class Box {\n"
        "    def __init__(value) { this.value = value }\n"
        "    def get() { this.value }\n"
        "    def class.make(value) { this(value) }\n"
        "}\n"
        "print(Box.make(3).get())\n"
    ),
    "val f = do(x) { x + 1 }\nprint(f(4))\n",
]


def _compile(source: str):
    return compile_module(lower_module(build_ast(source)))


def _run(program):
    interpreter = ASTInterpreter(CompilerErrorHandler())
    vm = BytecodeVM(interpreter)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), interpreter.runtime.activate():
        value = vm.run(program)
    return buf.getvalue(), value.host_value


def _structural(program):
    return [
        (
            proto.name,
            proto.params,
            proto.register_count,
            proto.local_count,
            proto.scratch_base,
            proto.code,
            proto.constants,
            proto.line_table,
            proto.has_this,
            proto.uses_cells,
            proto.defines_extensions,
            proto.signature,
        )
        for proto in (program.main, *program.functions)
    ]


@pytest.mark.parametrize("source", _PROGRAMS)
def test_round_trip_structure(source, tmp_path):
    program = _compile(source)
    path = tmp_path / "module.obc"
    write_obc(program, path)
    restored = read_obc(path)
    assert _structural(restored) == _structural(program)


@pytest.mark.parametrize("source", _PROGRAMS)
def test_round_trip_execution(source, tmp_path):
    program = _compile(source)
    path = tmp_path / "module.obc"
    write_obc(program, path)
    restored = read_obc(path)
    assert _run(restored) == _run(program)


def test_bad_magic_is_rejected(tmp_path):
    path = tmp_path / "bad.obc"
    path.write_bytes(b"NOPE\x00\x01")
    with pytest.raises(ObcError):
        read_obc(path)


def test_out_of_range_int_is_rejected(tmp_path):
    program = _compile("print(1)\n")
    huge = 1 << 70
    object.__setattr__(program.main, "constants", (huge,))
    with pytest.raises(ObcError):
        write_obc(program, tmp_path / "huge.obc")
