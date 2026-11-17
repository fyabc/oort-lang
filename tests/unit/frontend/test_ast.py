#! /usr/bin/env python

import pytest

from tests.helpers import TEST_ASSETS_DIR, get_compiler


def test_ast_string(capsys: pytest.CaptureFixture):
    test_string = "print(1 + 2)"
    compiler = get_compiler("NOT_EXIST -t ast")
    compiler.run_string(test_string)

    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
Module {
  (body): Block {
    (0): Call {
      (func): Name('print', ctx=LOAD) {}
      (arg 0): Argument {
        (value): BinaryExpr(op='+') {
          (lhs): Int(value=1) {}
          (rhs): Int(value=2) {}
        }
      }
    }
  }
}
"""
    )


@pytest.mark.parametrize("file_name", ["basic", "newline"])
def test_ast_file(file_name: str, capsys: pytest.CaptureFixture):
    test_file = TEST_ASSETS_DIR / f"{file_name}.ort"
    compiler = get_compiler(f"{test_file} -t ast")
    compiler.run_file(compiler.args.input_file)

    with open(TEST_ASSETS_DIR / f"{file_name}.ast", encoding="utf-8") as f:
        ast_string = f.read()
    captured = capsys.readouterr()
    assert captured.out == ast_string


def test_macro_expr(capsys: pytest.CaptureFixture):
    test_string = """\
2 + @max(a, (b, c)) * 3
"""
    compiler = get_compiler("NOT_EXIST -t ast")
    compiler.run_string(test_string)

    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
Module {
  (body): Block {
    (0): BinaryExpr(op='+') {
      (lhs): Int(value=2) {}
      (rhs): BinaryExpr(op='*') {
        (lhs): MacroCall(name='max') {
          (arg 0): Argument {
            (value): Name('a', ctx=LOAD) {}
          }
          (arg 1): Argument {
            (value): Tuple {
              (0): Name('b', ctx=LOAD) {}
              (1): Name('c', ctx=LOAD) {}
            }
          }
        }
        (rhs): Int(value=3) {}
      }
    }
  }
}
"""
    )


def test_macro_block(capsys: pytest.CaptureFixture):
    test_string = """
@no_stdout {
    print(4)
}
"""
    compiler = get_compiler("NOT_EXIST -t ast")
    compiler.run_string(test_string)

    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
Module {
  (body): Block {
    (0): MacroCall(name='no_stdout') {
      (arg 0): Argument {
        (value): Block {
          (0): Call {
            (func): Name('print', ctx=LOAD) {}
            (arg 0): Argument {
              (value): Int(value=4) {}
            }
          }
        }
      }
    }
  }
}
"""
    )


if __name__ == "__main__":
    pytest.main([__file__])
