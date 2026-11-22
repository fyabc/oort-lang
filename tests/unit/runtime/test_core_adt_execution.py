#! /usr/bin/env python

"""Runtime execution of `oort-core` enums and `match`."""

import pytest


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
        "enum IntMaybe { Just(value: Int), Nothing }\n"
        "def wrap(x: Int) -> IntMaybe { Just(x) }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import Just, Nothing, wrap\n'
        "val x = wrap(3)\n"
        "print(match x { Just(v) => v, Nothing => 0 })\n"
        "val y = Nothing\n"
        "print(match y { Just(v) => v, Nothing => 42 })\n",
        encoding="utf-8",
    )
    assert run_file(main).stdout == "3\n42\n"


def test_generic_enum_executes_on_both_backends(run_source):
    source = core(
        "enum Maybe[T] { Just(value: T), Nothing }\n"
        "enum Pair[A, B] { Pair(first: A, second: B) }\n"
        "def unwrap(o: Maybe[Int]) -> Int { match o { Just(v) => v, Nothing => 0 } }\n"
        "val a: Maybe[Int] = Just(2)\n"
        "print(unwrap(a), unwrap(Nothing))\n"
        'val p: Pair[Int, String] = Pair(1, "x")\n'
        "print(match p { Pair(n, s) => s })\n"
    )
    assert run_source(source, target="eval").stdout == "2 0\nx\n"
    assert run_source(source, target="vm").stdout == "2 0\nx\n"


def test_recursive_generic_enum_executes_on_both_backends(run_source):
    source = core(
        "enum MyList[T] { Cons(head: T, tail: MyList[T]), Nil }\n"
        "def total(xs: MyList[Int]) -> Int {\n"
        "    match xs { Cons(h, t) => h + total(t), Nil => 0 }\n"
        "}\n"
        "val xs: MyList[Int] = Cons(1, Cons(2, Nil))\n"
        "print(total(xs))\n"
    )
    assert run_source(source, target="eval").stdout == "3\n"
    assert run_source(source, target="vm").stdout == "3\n"


def test_full_patterns_on_both_backends(run_source):
    source = core(
        "enum Pair { P(a: Int, b: Int) }\n"
        "def f(n: Int, p: Pair) -> Int {\n"
        "    match n {\n"
        "        0 => 10,\n"
        "        1 | 2 => 20,\n"
        "        _ => match p { P(x, 0) | P(0, x) => x, P(x, y) => x + y }\n"
        "    }\n"
        "}\n"
        "def g(n: Int) -> Int {\n"
        "    match n { x if x > 10 => x, x if x < 0 => -x, _ => 0 }\n"
        "}\n"
        "def h(t: Tuple[Int, Bool]) -> Int {\n"
        "    match t {\n"
        "        (0, true) => 1,\n"
        "        (0, false) => 2,\n"
        "        (_, true) => 3,\n"
        "        (_, false) => 4\n"
        "    }\n"
        "}\n"
        "print(f(0, P(1, 2)), f(2, P(1, 2)), f(9, P(4, 0)), f(9, P(4, 3)))\n"
        "print(g(11), g(-3), g(5))\n"
        "print(h((0, true)), h((0, false)), h((5, true)), h((5, false)))\n"
    )
    expected = "10 20 4 7\n11 3 0\n1 2 3 4\n"
    assert run_source(source, target="eval").stdout == expected
    assert run_source(source, target="vm").stdout == expected


def test_builtin_option_and_result_on_both_backends(run_source):
    source = core(
        "val a: Option[Int] = Some(1)\n"
        "val n: Option[Int] = None\n"
        "val r: Result[Int, String] = Ok(2)\n"
        'val e: Result[Int, String] = Err("bad")\n'
        "print(match a { Some(v) => v, None => 0 })\n"
        "print(match n { Some(v) => v, None => -1 })\n"
        "print(match r { Ok(v) => v, Err(m) => 0 })\n"
        "print(match e { Ok(v) => v, Err(m) => len(m) })\n"
    )
    expected = "1\n-1\n2\n3\n"
    assert run_source(source, target="eval").stdout == expected
    assert run_source(source, target="vm").stdout == expected


def test_builtin_option_and_result_across_modules(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\n"
        "def wrap(x: Int) -> Option[Int] { Some(x) }\n"
        'def fail(x: Int) -> Result[Int, String] { Err("no") }\n',
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import wrap, fail\n'
        "val a = wrap(7)\n"
        "print(match a { Some(v) => v, None => 0 })\n"
        "val r = fail(1)\n"
        "print(match r { Ok(v) => v, Err(m) => len(m) })\n",
        encoding="utf-8",
    )
    assert run_file(main).stdout == "7\n2\n"


def test_prelude_constructors_are_not_module_exports(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\nval base: Int = 1\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import Some\nprint(1)\n',
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        run_file(main)


def test_generic_enum_across_modules(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\n"
        "enum LibMaybe[T] { Just(value: T), Nothing }\n"
        "def wrap(x: Int) -> LibMaybe[Int] { Just(x) }\n"
        "def nothing() -> LibMaybe[Int] { Nothing }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import wrap, nothing\n'
        "val a = wrap(7)\n"
        "print(match a { Just(v) => v, Nothing => 0 })\n"
        "val b = nothing()\n"
        "print(match b { Just(v) => v, Nothing => 0 })\n",
        encoding="utf-8",
    )
    assert run_file(main).stdout == "7\n0\n"


def test_module_namespace_adt_function(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\n"
        "enum IntMaybe { Just(value: Int), Nothing }\n"
        "def wrap(x: Int) -> IntMaybe { Just(x) }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nimport "./lib"\nprint(match lib.wrap(4) { Just(v) => v, Nothing => 0 })\n',
        encoding="utf-8",
    )
    assert run_file(main).stdout == "4\n"
