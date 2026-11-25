#! /usr/bin/env python

"""Typed core function values: named functions as first-class values (B2)."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler

FUNCTION_VALUES = """#lang oort-core

def inc(x: Int) -> Int { x + 1 }
def dec(x: Int) -> Int { x - 1 }

def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }
def pick(flag: Bool) -> (Int) -> Int { if flag { inc } else { dec } }
def local() -> Int { val f: (Int) -> Int = inc; f(10) }

def sum_apply(fs: List[(Int) -> Int], x: Int) -> Int {
    var total: Int = 0
    for f in fs { total = total + f(x) }
    total
}

def dispatch(op: String, x: Int) -> Int {
    val table: Dict[String, (Int) -> Int] = {: "inc": inc, "dec": dec :}
    val f: (Int) -> Int = table[op]
    f(x)
}

def with_lambda() -> Int {
    val double: (Int) -> Int = do(x: Int) -> Int { x * 2 }
    double(21)
}

def lambda_arg() -> Int {
    apply(do(x: Int) -> Int { x + 10 }, 5)
}

def lambda_in_list() -> Int {
    val fs: List[(Int) -> Int] = [do(x: Int) -> Int { x - 1 }, inc]
    var total: Int = 0
    for f in fs { total = total + f(10) }
    total
}

def nested_lambda() -> Int {
    val f: (Int) -> Int = do(x: Int) -> Int { apply(do(y: Int) -> Int { y * 3 }, x) }
    f(4)
}

print(apply(inc, 1), apply(dec, 1))
print(apply(pick(true), 2), apply(pick(false), 2))
print(local())
print(sum_apply([inc, dec], 10))
print(dispatch("inc", 6), dispatch("dec", 6))
print(with_lambda(), lambda_arg(), lambda_in_list(), nested_lambda())
"""

FUNCTION_VALUES_OUTPUT = "2 0\n3 1\n11\n20\n7 5\n42 15 20 12\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_named_function_values_match_across_targets(capsys, target):
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_string(FUNCTION_VALUES)
    assert capsys.readouterr().out == FUNCTION_VALUES_OUTPUT


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "def g() -> Int { val f = do: 1\nf() }\nprint(g())",
            "Lambdas without an explicit parameter list are not supported",
        ),
        (
            "def eq(f: (Int) -> Int, g: (Int) -> Int) -> Bool { f == g }\nprint(true)",
            "Operator '==' requires two numbers, two Bool or two String operands",
        ),
        (
            "def inc(x: Int) -> Int { x + 1 }\n"
            "def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }\n"
            "print(apply(inc, true))",
            "Expected Int, got Bool.",
        ),
    ],
)
def test_function_value_errors(caplog, source, message):
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises((SystemExit, CompilerError)):
        compiler.run_string("#lang oort-core\n" + source)
    assert message in caplog.text


CAPTURING = """#lang oort-core

def make_adder(n: Int) -> (Int) -> Int {
    do(x: Int) -> Int { x + n }
}

def use_adder() -> Int {
    val add10 = make_adder(10)
    add10(5)
}

def loop_capture() -> Int {
    var total = 0
    for i in [10, 20, 30] {
        val g = do(x: Int) -> Int { x + i }
        total = total + g(1)
    }
    total
}

def nested(a: Int) -> (Int) -> (Int) -> Int {
    do(b: Int) -> (Int) -> Int {
        do(c: Int) -> Int { a + b + c }
    }
}

def use_nested() -> Int {
    val step = nested(100)
    val partial = step(20)
    partial(3)
}

def shadow() -> Int {
    val n = 100
    val f = do(n: Int) -> Int { n * 2 }
    f(7) + n
}

def counter() -> () -> Int {
    var n = 0
    do() -> Int { n = n + 1; n }
}

def use_counter() -> Int {
    val c = counter()
    c() + c() + c()
}

def reassign_after_capture() -> Int {
    var k = 1
    val f = do(x: Int) -> Int { x + k }
    k = 2
    f(10)
}

def make_acc() -> Int {
    var sum = 0
    val add = do(v: Int) -> Unit { sum = sum + v }
    add(1)
    add(20)
    add(300)
    sum
}

print(use_adder(), loop_capture(), use_nested(), shadow())
print(use_counter(), reassign_after_capture(), make_acc())
"""

CAPTURING_OUTPUT = "15 63 123 114\n6 12 321\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_capturing_closures_match_across_targets(capsys, target):
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_string(CAPTURING)
    assert capsys.readouterr().out == CAPTURING_OUTPUT


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_top_level_block_capture_shares_main_cell(capsys, target):
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_string(
        "#lang oort-core\n"
        "{\n"
        "    var n = 0\n"
        "    val c = do() -> Int { n = n + 1; n }\n"
        "    print(c(), c(), n)\n"
        "}\n"
    )
    assert capsys.readouterr().out == "1 2 2\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_lambda_survives_module_linking(capsys, target, tmp_path):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        "#lang oort-core\n"
        "def twice(f: (Int) -> Int, x: Int) -> Int { f(f(x)) }\n"
        "def lib_lambda() -> Int { twice(do(v: Int) -> Int { v + 3 }, 4) }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import twice, lib_lambda\n'
        "def main_lambda() -> Int { twice(do(v: Int) -> Int { v * 2 }, 5) }\n"
        "print(lib_lambda(), main_lambda())\n",
        encoding="utf-8",
    )

    compiler = get_compiler(["-t", target, "NOT_EXIST", str(main)])
    compiler.run_file(main)
    assert capsys.readouterr().out == "10 20\n"
