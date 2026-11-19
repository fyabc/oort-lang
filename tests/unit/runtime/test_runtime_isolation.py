#! /usr/bin/env python

"""Each interpreter owns an isolated type system and runtime singletons."""

from oort_lang.driver.compiler import Compiler
from oort_lang.runtime import OortBool, OortInt, OortNull, Runtime, get_runtime
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.semantics.pass1 import Pass1Analyzer
from oort_lang.source.input_info import StringInputInfo
from tests.helpers import get_compiler


def _run_source(compiler: Compiler, interpreter: ASTInterpreter, source: str):
    input_info = StringInputInfo(source)
    parser = compiler._build_parser(input_info)
    ast = compiler.build_ast(parser, input_info)
    assert ast is not None
    ast = compiler.semantic_analyze(ast, Pass1Analyzer(compiler.error_handler, input_info))
    assert ast is not None
    return interpreter.run(ast)


def test_runtimes_have_independent_type_objects():
    runtime_a = Runtime()
    runtime_b = Runtime()

    with runtime_a.activate():
        assert get_runtime() is runtime_a
        int_a = OortInt(1)
        null_a = OortNull.get_null_value()
        true_a = OortBool.get_true_value()

    with runtime_b.activate():
        assert get_runtime() is runtime_b
        int_b = OortInt(1)
        null_b = OortNull.get_null_value()
        true_b = OortBool.get_true_value()

    assert int_a.type is runtime_a.types.int_type
    assert int_b.type is runtime_b.types.int_type
    assert int_a.type is not int_b.type
    assert null_a is runtime_a.null
    assert null_b is runtime_b.null
    assert null_a is not null_b
    assert true_a is runtime_a.true
    assert true_b is runtime_b.true
    assert true_a is not true_b


def test_existing_interpreter_is_not_affected_by_a_new_one():
    compiler = get_compiler("NOT_EXIST -t eval")
    interpreter_a = ASTInterpreter(compiler.error_handler)
    interpreter_b = ASTInterpreter(compiler.error_handler)

    int_type_a = _run_source(compiler, interpreter_a, "type(1)")
    int_type_b = _run_source(compiler, interpreter_b, "type(2)")

    assert int_type_a.name == "Int"
    assert int_type_b.name == "Int"
    assert int_type_a is not int_type_b

    # Creating and running interpreter B must not replace A's runtime types.
    assert _run_source(compiler, interpreter_a, "type(3)") is int_type_a
    assert _run_source(compiler, interpreter_a, "1 + 2").host_value == 3


def test_module_cache_is_per_interpreter(tmp_path, capsys):
    (tmp_path / "lib.ort").write_text('print("loaded")\nvar value = 1\n', encoding="utf-8")
    main = tmp_path / "main.ort"
    main.write_text('import "./lib"\nprint(lib.value)\n', encoding="utf-8")

    get_compiler("NOT_EXIST -t eval").run_file(main)
    get_compiler("NOT_EXIST -t eval").run_file(main)

    assert capsys.readouterr().out == "loaded\n1\nloaded\n1\n"
