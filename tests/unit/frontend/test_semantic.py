#! /usr/bin/env python

import pytest

from tests.helpers import get_compiler


def test_name_resolving(capsys: pytest.CaptureFixture):
    test_string = """\
var a = "global"
{
  def showA {
    print(a)
  }

  showA()
  var a = "block"
  showA()
}
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "global\nglobal\n"


def test_name_resolving2(capsys: pytest.CaptureFixture):
    test_string = """\
var a = 1
print("A1", a)
a = 2
print("A2", a)
{
  print("A3", a)
  var a = 3
  print("A4", a)
  a = 4
  print("A5", a)
}
print("A6", a)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "A1 1\nA2 2\nA3 2\nA4 3\nA5 4\nA6 2\n"


def test_name_in_own_initializer(caplog: pytest.LogCaptureFixture):
    test_string = """\
var a = 1
{ var a = a }
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(test_string)
    assert (
        caplog.text
        == """\
<string>:2:11: OortNameError: Can't read local variable a in its own initializer.
{ var a = a }
          ^
1 error generated.
0 warnings generated.
"""
    )


def test_local_redefinition(caplog: pytest.LogCaptureFixture):
    test_string = """\
var a = 1
var a = 2
{
    var b = 3
    var b = 4
}
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(test_string)
    assert (
        caplog.text
        == """\
<string>:5:9: OortNameError: Variable b is already defined.
    var b = 4
        ^
1 error generated.
0 warnings generated.
"""
    )


def test_bad_this(caplog: pytest.LogCaptureFixture):
    test_string = """\
this
def f { this }
class C { this }
class D { def g { this } }
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(test_string)
    assert (
        caplog.text
        == """\
<string>:1:1: OortNameError: Can't access 'this' outside method.
this
^^^^
<string>:2:9: OortNameError: Can't access 'this' outside method.
def f { this }
        ^^^^
<string>:3:11: OortNameError: Can't access 'this' outside method.
class C { this }
          ^^^^
3 errors generated.
0 warnings generated.
"""
    )


def test_return_in_initializer(caplog: pytest.LogCaptureFixture):
    test_string = """\
class C {
    def __init__ {
        return 1
    }
}
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(test_string)
    assert (
        caplog.text
        == """\
<string>:3:9: OortSyntaxError: Return inside method initializer.
        return 1
        ^^^^^^^^
1 error generated.
0 warnings generated.
"""
    )


def test_bad_super(caplog: pytest.LogCaptureFixture):
    test_string = """\
super
def f { super }
class C { super }
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(test_string)
    assert (
        caplog.text
        == """\
<string>:1:1: OortNameError: Can't use implicit 'super' outside method.
super
^^^^^
<string>:2:9: OortNameError: Can't use implicit 'super' outside method.
def f { super }
        ^^^^^
<string>:3:11: OortNameError: Can't use implicit 'super' outside method.
class C { super }
          ^^^^^
3 errors generated.
0 warnings generated.
"""
    )


@pytest.mark.parametrize(
    ("keyword", "message"),
    [("break", "Break outside loop."), ("continue", "Continue outside loop.")],
)
def test_loop_control_cannot_cross_function_boundary(
    keyword: str, message: str, caplog: pytest.LogCaptureFixture
):
    test_string = f"""\
while true {{
    def f {{ {keyword} }}
    f()
}}
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(test_string)
    assert message in caplog.text
