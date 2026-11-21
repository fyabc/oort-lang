#! /usr/bin/env python

"""Runtime execution of `oort-core` enums and `match`."""


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def test_enum_construction_and_match(run_source):
    result = run_source(
        core(
            "enum Shape { Circle(r: Int), Rect(w: Int, h: Int), Empty }\n"
            "val s = Circle(3)\n"
            "print(match s { Circle(r) => r, Rect(w, h) => w * h, Empty => 0 })\n"
        )
    )
    assert result.stdout == "3\n"


def test_nullary_constructors_and_wildcard(run_source):
    result = run_source(
        core(
            "enum Color { Red, Green }\n"
            "print(match Green { Red => 1, Green => 2 })\n"
            "print(match Red { _ => 9 })\n"
        )
    )
    assert result.stdout == "2\n9\n"


def test_enum_values_print(run_source):
    result = run_source(core("enum E { A, B(x: Int) }\nprint(A)\nprint(B(2))\n"))
    assert result.stdout == "A\nB(2)\n"


def test_recursive_enum(run_source):
    result = run_source(
        core(
            "enum IntList { Cons(head: Int, tail: IntList), Nil }\n"
            "val xs = Cons(1, Cons(2, Nil))\n"
            "def total(xs: IntList) -> Int { match xs "
            "{ Cons(h, t) => h + total(t), Nil => 0 } }\n"
            "print(total(xs))\n"
        )
    )
    assert result.stdout == "3\n"


def test_nested_match(run_source):
    result = run_source(
        core(
            "enum Inner { A(x: Int), B }\n"
            "enum Outer { Wrap(inner: Inner), Empty }\n"
            "val o = Wrap(A(7))\n"
            "print(match o { Wrap(inner) => match inner { A(v) => v, B => 0 }, "
            "Empty => -1 })\n"
        )
    )
    assert result.stdout == "7\n"


def test_return_from_match_arm(run_source):
    result = run_source(
        core(
            "enum E { A, B }\n"
            "def f(x: E) -> Int { match x { A => return 1, B => 2 } }\n"
            "print(f(A))\nprint(f(B))\n"
        )
    )
    assert result.stdout == "1\n2\n"


def test_adt_constructors_and_match_across_modules(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\n"
        "enum IntOption { Some(value: Int), None }\n"
        "def wrap(x: Int) -> IntOption { Some(x) }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import Some, None, wrap\n'
        "val x = wrap(3)\n"
        "print(match x { Some(v) => v, None => 0 })\n"
        "val y = None\n"
        "print(match y { Some(v) => v, None => 42 })\n",
        encoding="utf-8",
    )
    assert run_file(main).stdout == "3\n42\n"


def test_module_namespace_adt_function(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\n"
        "enum IntOption { Some(value: Int), None }\n"
        "def wrap(x: Int) -> IntOption { Some(x) }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nimport "./lib"\nprint(match lib.wrap(4) { Some(v) => v, None => 0 })\n',
        encoding="utf-8",
    )
    assert run_file(main).stdout == "4\n"
