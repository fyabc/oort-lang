#! /usr/bin/env python

"""Basic statements: while loops and augmented assignment."""


def test_while_control_flow(run_source):
    out = run_source(
        """\
var i = 0
while i < 10 {
    i = i + 1
    if i == 5: continue
    if i == 8: break
    print(i)
}
"""
    ).stdout
    assert out == "1\n2\n3\n4\n6\n7\n"


def test_augmented_assignment(run_source):
    out = run_source(
        """\
var a = 1
a += 2
a *= 3
a -= 1
a /= 4
print(a)
var l = [1]
l += [2]
print(l)
var s = "a"
s += "b"
print(s)
""",
    ).stdout
    assert out == "2.0\n[1, 2]\nab\n"


def test_bitwise_operators(run_source):
    out = run_source("print(6 & 3, 6 | 3, 6 ^ 3, 1 << 3, 8 >> 1, ~0)\n").stdout
    assert out == "2 7 5 8 4 -1\n"
