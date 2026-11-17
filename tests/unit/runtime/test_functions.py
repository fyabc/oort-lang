#! /usr/bin/env python

import pytest

from tests.helpers import get_compiler


def test_call_with_block(capsys: pytest.CaptureFixture):
    test_string = """\
def decorate(arg, f) {
    print("Before call")
    var result = f(arg)
    print("After call")
    result
}
var ret = decorate("Oort!") do arg {
    print("Hello,", arg)
    arg
}
print(ret)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "Before call\nHello, Oort!\nAfter call\nOort!\n"


def test_recursion(capsys: pytest.CaptureFixture):
    test_string = """\
def exp(a, n) {
    if n == 0: return 1
    a * exp(a, n - 1)
}
exp(3, 4)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    result = compiler.run_string(test_string)
    assert result == 81


def test_closure(capsys: pytest.CaptureFixture):
    test_string = """\
def makeCounter {
    var i = 0
    def count {
        i = i + 1
        print(i)
    }
    count
}
val count = makeCounter()
count()
count()
count()
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n3\n"


if __name__ == "__main__":
    pytest.main([__file__])
