#! /usr/bin/env python

"""Runtime behavior of function types, lambdas and function values."""


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def test_inferred_lambda_and_closure(run_source):
    result = run_source(
        core(
            "val inc = do(x: Int) -> Int { x + 1 }\n"
            "def make(n: Int) -> (Int) -> Int { do(x: Int) -> Int { x + n } }\n"
            "val add10 = make(10)\n"
            "print(inc(2))\nprint(add10(5))\n"
        )
    )
    assert result.stdout == "3\n15\n"


def test_higher_order_function(run_source):
    result = run_source(
        core(
            "def apply_twice(f: (Int) -> Int, x: Int) -> Int { f(f(x)) }\n"
            "print(apply_twice(do(x: Int) -> Int { x + 3 }, 1))\n"
        )
    )
    assert result.stdout == "7\n"


def test_unit_function_value(run_source):
    result = run_source(
        core("val show: (Int) -> Unit = do(x: Int) -> Unit { print(x) }\nshow(7)\n")
    )
    assert result.stdout == "7\n"
    assert result.value is None


def test_function_value_exported_from_module(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\nval inc: (Int) -> Int = do(x: Int) -> Int { x + 1 }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import inc\nprint(inc(4))\n',
        encoding="utf-8",
    )
    assert run_file(main).stdout == "5\n"


def test_function_value_in_adt_payload(run_source):
    result = run_source(
        core(
            "enum Box { Box(run: (Int) -> Int), Empty }\n"
            "val b = Box(do(x: Int) -> Int { x * 2 })\n"
            "print(match b { Box(f) => f(3), Empty => 0 })\n"
        )
    )
    assert result.stdout == "6\n"
