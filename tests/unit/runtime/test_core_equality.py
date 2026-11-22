#! /usr/bin/env python

"""Runtime equality for `oort-core` ADTs and static class instances."""


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def test_adt_equality_and_keys_on_both_backends(run_source):
    source = core(
        """enum Color { Red, Green }
val a = Some(1)
val b = Some(1)
val c = Some(2)
val xs: List[Option[Int]] = [Some(1), None]
val ys: List[Option[Int]] = [Some(1), None]
val d: Dict[Color, Int] = {: Red: 1, Green: 2 :}
val s: Set[Color] = {. Red, Green .}
print(a == b, a == c, a != b)
print(xs == ys)
print(d[Red], s == {. Green, Red .})
"""
    )
    expected = "true false false\ntrue\n1 true\n"
    assert run_source(source, target="eval").stdout == expected
    assert run_source(source, target="vm").stdout == expected


def test_class_identity_equality_on_both_backends(run_source):
    source = core(
        """class C {
    val x: Int

    def __init__(x: Int) {
        this.x = x
    }
}
val a = C(1)
val b = C(1)
val d: Dict[C, Int] = {: a: 7 :}
print(a == a, a == b, a != b)
print(d[a], [a] == [a], [a] == [C(1)])
"""
    )
    expected = "true false true\n7 true false\n"
    assert run_source(source, target="eval").stdout == expected
    assert run_source(source, target="vm").stdout == expected


def test_prelude_option_equality_across_modules(tmp_path, run_file):
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\ndef wrap(x: Int) -> Option[Int] {\n    Some(x)\n}\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import wrap\n'
        "val a = wrap(1)\n"
        "val b: Option[Int] = Some(1)\n"
        "print(a == b, a != b)\n",
        encoding="utf-8",
    )
    assert run_file(main).stdout == "true false\n"
