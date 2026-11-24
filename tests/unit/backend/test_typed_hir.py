#! /usr/bin/env python

"""Typed HIR model, subset lowering, validation and dump (design 15, M1)."""

import pytest

from oort_lang.bytecode import (
    TypedCodeVM,
    TypedOp,
    compile_module,
    compile_typed_module,
    disassemble_typed_program,
    read_typed_obc,
    write_typed_obc,
)
from oort_lang.bytecode.serialize import ObcError, read_obc, write_obc
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.diagnostics.syntax_errors import UnsupportedSyntax
from oort_lang.driver.compiler import CompilerError
from oort_lang.hir import AdtType, ContainerType, IrType, lower_module, lower_typed_module
from oort_lang.hir.typed_link import load_typed_units
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.source.input_info import StringInputInfo
from tests.helpers import EXAMPLES_DIR, build_ast, get_compiler

FIB = """\
#lang oort-core

def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}

print(fib(10))
"""

EARLY_RETURN = """\
#lang oort-core

def clamp(x: Int) -> Int {
    if x < 0 { return 0 }
    return x
}

print(clamp(-1))
"""

LOOP = """\
#lang oort-core

def total(n: Int) -> Int {
    var sum: Int = 0
    var i: Int = 0
    while i < n {
        sum = sum + i
        i = i + 1
    }
    return sum
}

print(total(5))
"""


def test_typed_lowering_attaches_signatures_and_register_types():
    typed = lower_typed_module(build_ast(FIB))
    fib = next(function for function in typed.functions if function.hir.name == "fib")

    assert typed.main.param_types == ()
    assert typed.main.ret_type is IrType.UNIT
    assert fib.param_types == (IrType.INT,)
    assert fib.ret_type is IrType.INT
    assert len(fib.register_types) == fib.hir.local_count
    assert IrType.BOOL in fib.register_types
    assert IrType.FUNCTION in fib.register_types


@pytest.mark.parametrize("source", [FIB, EARLY_RETURN, LOOP])
def test_typed_lowering_accepts_scalar_subset(source: str):
    typed = lower_typed_module(build_ast(source))
    assert typed.main.ret_type is IrType.UNIT
    assert typed.functions


def test_thir_target_prints_types(capsys: pytest.CaptureFixture):
    compiler = get_compiler("NOT_EXIST -t thir")
    compiler.run_string(FIB)

    captured = capsys.readouterr()
    assert "<main>() -> Unit local_count=" in captured.out
    assert "fib(n: Int) -> Int local_count=" in captured.out
    assert "; R" in captured.out
    assert ":Bool" in captured.out
    assert ":Int" in captured.out


def test_typed_subset_example_is_accepted():
    source = (EXAMPLES_DIR / "08_core/08_15_typed_subset.ort").read_text(encoding="utf-8")
    typed = lower_typed_module(build_ast(source))

    names = {function.hir.name for function in typed.functions}
    assert {"fact", "fib", "clamp", "sum_to", "sign", "average", "mixed"} <= names


@pytest.mark.parametrize(
    "name",
    [
        "08_15_typed_subset.ort",
        "08_16_typed_collections.ort",
        "08_17_typed_sets_dicts.ort",
        "08_18_typed_adts.ort",
        "08_19_typed_generic_adts.ort",
        "08_20_typed_modules.ort",
        "08_21_typed_collection_surface.ort",
        "08_22_typed_function_values.ort",
        "08_10_patterns.ort",
    ],
)
def test_tvm_matches_vm_on_example(name: str, run_file):
    path = EXAMPLES_DIR / "08_core" / name
    typed = run_file(path, target="tvm")
    vm = run_file(path, target="vm")

    assert typed.stdout == vm.stdout
    assert typed.value == vm.value


@pytest.mark.parametrize("source", [FIB, EARLY_RETURN, LOOP])
def test_tvm_matches_vm_on_inline_programs(
    source: str,
    capsys: pytest.CaptureFixture,
):
    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out


def test_typed_main_value_uses_last_expression_type():
    source = """\
#lang oort-core
def add(a: Int, b: Int) -> Int { a + b }
add(2, 3)
"""
    typed = lower_typed_module(build_ast(source))
    assert typed.main.ret_type is IrType.INT

    compiler = get_compiler("NOT_EXIST -t tvm")
    assert compiler.run_string(source) == 5


def test_typed_bytecode_uses_typed_opcodes():
    typed = lower_typed_module(
        build_ast(
            """\
#lang oort-core
def mixed(a: Int, b: Float) -> Float { a + b }
def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}
print(mixed(1, 2.5))
"""
        )
    )
    program = compile_typed_module(typed)
    ops = {TypedOp(word >> 24) for word in program.main.code}
    for proto in program.functions:
        ops |= {TypedOp(word >> 24) for word in proto.code}

    assert TypedOp.ADD_I in ops
    assert TypedOp.ADD_F in ops
    assert TypedOp.TO_FLOAT in ops
    assert TypedOp.JMP_FALSE in ops
    assert TypedOp.CALL in ops


def test_tbc_target_prints_typed_disassembly(capsys: pytest.CaptureFixture):
    compiler = get_compiler("NOT_EXIST -t tbc")
    compiler.run_string(FIB)

    captured = capsys.readouterr()
    assert "CALL" in captured.out
    assert "JMP_FALSE" in captured.out
    assert "register types:" in captured.out


def test_tbc_disassembles_the_program_tvm_runs(
    tmp_path, run_file, capsys: pytest.CaptureFixture, monkeypatch
):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        """#lang oort-core
enum Color { Red, Green }
def add(a: Int, b: Int) -> Int { a + b }
def make() -> Color { Green }
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        """#lang oort-core
enum Shape { Circle }
from "./lib" import add, make
print(add(1, 2), make(), Circle)
""",
        encoding="utf-8",
    )

    captured = {}
    original_run = TypedCodeVM.run

    def capture(self, program):
        captured["program"] = program
        return original_run(self, program)

    monkeypatch.setattr(TypedCodeVM, "run", capture)
    run_file(main, target="tvm")
    capsys.readouterr()

    expected = disassemble_typed_program(captured["program"])
    tbc = run_file(main, target="tbc")
    assert tbc.stdout == expected + "\n"


def test_typed_obc_round_trip(tmp_path):
    source = FIB.replace("print(fib(10))", "fib(10)")
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    path = tmp_path / "typed.obc"
    write_typed_obc(program, path)

    loaded = read_typed_obc(path)

    assert loaded.main.code == program.main.code
    assert loaded.main.constants == program.main.constants
    assert loaded.main.register_types == program.main.register_types
    assert loaded.main.param_types == program.main.param_types
    assert loaded.main.ret_type == program.main.ret_type
    assert loaded.functions[0].code == program.functions[0].code

    result = TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert result.host_value == 55


def test_typed_obc_rejects_dynamic_kind(tmp_path):
    erased = compile_module(lower_module(build_ast(FIB)))
    path = tmp_path / "dynamic.obc"
    write_obc(erased, path)

    with pytest.raises(ObcError, match="kind=1"):
        read_typed_obc(path)


def test_dynamic_obc_rejects_typed_kind(tmp_path):
    program = compile_typed_module(lower_typed_module(build_ast(FIB)))
    path = tmp_path / "typed.obc"
    write_typed_obc(program, path)

    with pytest.raises(ObcError):
        read_obc(path)


def test_typed_mixed_comparison_is_exact(capsys: pytest.CaptureFixture):
    source = """\
#lang oort-core

def same(big: Int, f: Float) -> Bool { big == f }

print(same(9007199254740993, 9007199254740992.0))
print(same(9007199254740992, 9007199254740992.0))
"""
    typed = lower_typed_module(build_ast(source))
    program = compile_typed_module(typed)
    ops = {
        TypedOp(word >> 24) for proto in (program.main, *program.functions) for word in proto.code
    }
    assert TypedOp.EQ_MIXED in ops

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "false\ntrue\n"


def test_typed_string_subset(capsys: pytest.CaptureFixture):
    source = """\
#lang oort-core

def greet(name: String) -> String { "Hello, " + name }
def before(a: String, b: String) -> Bool { a < b }

print(greet("Oort"))
print(len("abc"), len(""))
print("a" < "b", "a" == "a", "a" != "b")
print(before("b", "a"))
"""
    typed = lower_typed_module(build_ast(source))
    program = compile_typed_module(typed)
    ops = {
        TypedOp(word >> 24) for proto in (program.main, *program.functions) for word in proto.code
    }
    assert TypedOp.ADD_S in ops
    assert TypedOp.LT_S in ops

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "Hello, Oort\n3 0\ntrue true true\nfalse\n"


def test_typed_collections(capsys: pytest.CaptureFixture):
    source = """\
#lang oort-core

def first(xs: List[Int]) -> Int { xs[0] }
def pair(a: Int, b: String) -> Tuple[Int, String] { (a, b) }

print([1, 2, 3])
print(len([1, 2, 3]))
print(first([4, 5]))
print(pair(7, "x"))
print([1, 2] == [1, 2], [1, 2] != [1, 3])
"""
    typed = lower_typed_module(build_ast(source))
    program = compile_typed_module(typed)
    ops = {
        TypedOp(word >> 24) for proto in (program.main, *program.functions) for word in proto.code
    }
    assert TypedOp.NEW_LIST in ops
    assert TypedOp.NEW_TUPLE in ops
    assert TypedOp.GET_ITEM in ops
    assert TypedOp.EQ_LIST in ops

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "[1, 2, 3]\n3\n4\n(7, x)\ntrue true\n"


def test_typed_for_loops(capsys: pytest.CaptureFixture, tmp_path):
    source = """\
#lang oort-core

def total(xs: List[Int]) -> Int {
    var sum: Int = 0
    for x in xs { sum = sum + x }
    sum
}

def tuple_total(xs: Tuple[Int, Int, Int]) -> Int {
    var sum: Int = 0
    for x in xs { sum = sum + x }
    sum
}

def last_char(s: String) -> String {
    var out: String = ""
    for ch in s { out = ch }
    out
}

print(total([1, 2, 3, 4]))
print(tuple_total((5, 6, 7)))
print(last_char("Oort"))
"""
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    ops = {
        TypedOp(word >> 24) for proto in (program.main, *program.functions) for word in proto.code
    }
    assert TypedOp.OPEN_ITER in ops
    assert TypedOp.ITER_NEXT in ops
    assert any(IrType.ITERATOR in proto.types for proto in (program.main, *program.functions))

    path = tmp_path / "for_loops.obc"
    write_typed_obc(program, path)
    loaded = read_typed_obc(path)
    assert any(IrType.ITERATOR in proto.types for proto in (loaded.main, *loaded.functions))

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "10\n18\nt\n"


def test_typed_for_rejects_heterogeneous_tuple_iteration():
    source = """\
#lang oort-core

def first(xs: Tuple[Int, String]) -> Int {
    var out: Int = 0
    for x in xs { out = 1 }
    out
}

print(first((1, "a")))
"""
    with pytest.raises(SystemExit):
        get_compiler("NOT_EXIST -t tvm").run_string(source)


def test_typed_sets_and_dicts(capsys: pytest.CaptureFixture, tmp_path):
    source = """#lang oort-core

def dict_total(items: Dict[String, Int]) -> Int {
    var total: Int = 0
    for key in items { total = total + items[key] }
    total
}

def set_total(items: Set[Int]) -> Int {
    var total: Int = 0
    for item in items { total = total + item }
    total
}

def tuple_key(items: Dict[Tuple[Int, Bool], String]) -> String { items[(1, true)] }

def float_key(items: Dict[Float, String]) -> String { items[1.5] }

print({: "a": 1, "b": 2 :}["b"], len({: "a": 1, "b": 2 :}))
print(dict_total({: "a": 1, "b": 2 :}))
print(set_total({. 2, 4, 6 .}), len({. 2, 4, 6 .}))
print({: "a": 1 :} == {: "a": 1 :}, {. 1, 2 .} == {. 2, 1 .})
print({: "x": (1, true) :})
print(tuple_key({: (1, true): "yes", (2, false): "no" :}))
print(float_key({: 1.5: "ok", 2.5: "no" :}))
print(len({. (1, 2), (2, 3), (1, 2) .}))
"""
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    ops = {
        TypedOp(word >> 24) for proto in (program.main, *program.functions) for word in proto.code
    }
    assert TypedOp.NEW_SET in ops
    assert TypedOp.NEW_DICT in ops
    assert TypedOp.EQ_SET in ops
    assert TypedOp.EQ_DICT in ops
    assert TypedOp.OPEN_ITER in ops

    path = tmp_path / "sets_dicts.obc"
    write_typed_obc(program, path)
    loaded = read_typed_obc(path)
    loaded_types = {
        ir_type for proto in (loaded.main, *loaded.functions) for ir_type in proto.types
    }
    assert any(
        isinstance(ir_type, ContainerType) and ir_type.kind == "Set" for ir_type in loaded_types
    )
    assert any(
        isinstance(ir_type, ContainerType) and ir_type.kind == "Dict" for ir_type in loaded_types
    )

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "2 2\n3\n12 3\ntrue true\n{: x: (1, true) :}\nyes\nok\n2\n"


def test_typed_monomorphic_adts(capsys: pytest.CaptureFixture, tmp_path):
    source = """#lang oort-core

enum Shape {
    Circle(radius: Int),
    Rect(width: Int, height: Int),
    Empty,
}

enum Tree {
    Leaf(value: Int),
    Node(left: Tree, right: Tree),
}

def area(shape: Shape) -> Int {
    match shape {
        Circle(r) => r * r * 3,
        Rect(w, h) => w * h,
        Empty => 0,
    }
}

def tree_sum(tree: Tree) -> Int {
    match tree {
        Leaf(value) => value,
        Node(left, right) => tree_sum(left) + tree_sum(right),
    }
}

print(area(Circle(2)), area(Rect(3, 4)), area(Empty))
print(tree_sum(Node(Leaf(1), Node(Leaf(2), Leaf(3)))))
print(Circle(2) == Circle(2), Circle(2) == Circle(3))
print(Circle(2))
"""
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    ops = {
        TypedOp(word >> 24) for proto in (program.main, *program.functions) for word in proto.code
    }
    assert TypedOp.NEW_ADT in ops
    assert TypedOp.ADT_TAG in ops
    assert TypedOp.ADT_FIELD in ops
    assert TypedOp.EQ_ADT in ops

    path = tmp_path / "adts.obc"
    write_typed_obc(program, path)
    loaded = read_typed_obc(path)
    decls = {decl.name: decl for decl in loaded.adt_decls}
    assert {"Shape", "Tree"} <= decls.keys()
    assert decls["Shape"].constructors[0].arity == 1

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "12 12 0\n6\ntrue false\nCircle(2)\n"


def test_typed_generic_adts(capsys: pytest.CaptureFixture, tmp_path):
    source = """#lang oort-core

enum Maybe[T] {
    Just(value: T),
    Nothing,
}

def unwrap(value: Maybe[Int], fallback: Int) -> Int {
    match value {
        Just(v) => v,
        Nothing => fallback,
    }
}

print(unwrap(Just(7), 0))
print(unwrap(Nothing, 9))
print(unwrap(Just(3), 9) + unwrap(Nothing, 4))
"""
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    path = tmp_path / "generic_adts.obc"
    write_typed_obc(program, path)
    loaded = read_typed_obc(path)
    loaded_adts = [ir_type for ir_type in loaded.main.types if isinstance(ir_type, AdtType)]
    assert any(ir_type.args == (IrType.INT,) for ir_type in loaded_adts)

    result = TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert result.host_value is None
    capsys.readouterr()  # drop the round-trip run's output

    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "7\n9\n7\n"


def test_typed_generic_prelude_option(capsys: pytest.CaptureFixture):
    source = """#lang oort-core

def unwrap(value: Option[Int], fallback: Int) -> Int {
    match value {
        Some(v) => v,
        None => fallback,
    }
}

print(unwrap(Some(7), 0), unwrap(None, 9))
"""
    compiler = get_compiler("NOT_EXIST -t tvm")
    compiler.run_string(source)
    assert capsys.readouterr().out == "7 9\n"


def test_typed_literal_and_heterogeneous_tuple_patterns(capsys: pytest.CaptureFixture):
    source = """#lang oort-core

def classify_text(s: String) -> Int {
    match s {
        "a" => 1,
        "b" => 2,
        _ => 0,
    }
}

def flag(b: Bool) -> Int {
    match b {
        true => 1,
        false => 0,
    }
}

def pair(p: Tuple[Int, String]) -> Bool {
    match p {
        (0, "x") => true,
        _ => false,
    }
}

print(classify_text("a"), classify_text("b"), classify_text("z"))
print(flag(true), flag(false))
print(pair((0, "x")), pair((0, "y")), pair((1, "x")))
"""
    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out == "1 2 0\n1 0\ntrue false false\n"


def test_typed_core_from_imports(tmp_path, run_file):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        """#lang oort-core
enum Color { Red, Green }
def add(a: Int, b: Int) -> Int { a + b }
def make_red() -> Color { Red }
def paint(color: Color) -> Int { match color { Red => 1, Green => 2 } }
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        """#lang oort-core
from "./lib" import add, make_red, paint
def use() -> Int { add(1, 2) }
print(use())
print(add(4, 5))
print(make_red())
print(paint(make_red()))
""",
        encoding="utf-8",
    )

    typed = run_file(main, target="tvm")
    vm = run_file(main, target="vm")
    assert typed.stdout == vm.stdout == "3\n9\nRed\n1\n"


def test_typed_core_namespace_imports(tmp_path, run_file):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        """#lang oort-core
enum Color { Red, Green }
def add(a: Int, b: Int) -> Int { a + b }
def make_red() -> Color { Red }
def paint(color: Color) -> Int { match color { Red => 1, Green => 2 } }
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        """#lang oort-core
import "./lib"
def use() -> Int { lib.add(1, 2) }
def make() -> lib.Color { lib.make_red() }
print(use())
print(lib.add(4, 5))
print(lib.paint(make()))
""",
        encoding="utf-8",
    )

    typed = run_file(main, target="tvm")
    vm = run_file(main, target="vm")
    assert typed.stdout == vm.stdout == "3\n9\n1\n"


def _parse_only(source: str):
    compiler = get_compiler("NOT_EXIST -t eval")
    info = StringInputInfo(source)
    compiler.error_handler.register_input(info)
    dialect = compiler._resolve_dialect(info)
    assert dialect is not None
    ast = compiler.build_ast(compiler._build_parser(info), info, dialect=dialect)
    assert ast is not None
    return ast


LIB_SOURCE = """#lang oort-core
enum Color { Red, Green }
def add(a: Int, b: Int) -> Int { a + b }
def make_red() -> Color { Red }
"""


def _load_sources(tmp_path, main_source: str, lib_source: str = LIB_SOURCE):
    lib_path = tmp_path / "lib.ort"
    main_path = tmp_path / "main.ort"
    lib_ast = build_ast(lib_source)
    main_ast = _parse_only("#lang oort-core\n" + main_source)

    def resolve(spec: str, importer, position):
        if spec == "./lib":
            return lib_path, lib_ast
        return None

    return load_typed_units(main_ast, main_path, resolve)


def test_typed_link_rejects_missing_export(tmp_path):
    with pytest.raises(UnsupportedSyntax, match=r"Module 'lib' does not export 'missing'\."):
        _load_sources(tmp_path, 'from "./lib" import missing\nprint(1)\n')


def test_typed_link_rejects_type_only_export(tmp_path):
    with pytest.raises(UnsupportedSyntax, match="type-only export from 'lib'"):
        _load_sources(tmp_path, 'from "./lib" import Color\nprint(1)\n')


def test_typed_imported_constructors_run(tmp_path, run_file):
    lib = tmp_path / "lib.ort"
    lib.write_text(
        """#lang oort-core
enum Color { Red, Green }
enum Shape { Circle(radius: Int), Dot }
def make_red() -> Color { Red }
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        """#lang oort-core
import "./lib"
from "./lib" import Red, Green, Circle, Dot, make_red
def area(shape: lib.Shape) -> Int { match shape { Circle(r) => r * r, Dot => 0 } }
print(Red, Green, make_red())
print(area(Circle(3)), area(Dot))
""",
        encoding="utf-8",
    )

    typed = run_file(main, target="tvm")
    vm = run_file(main, target="vm")
    assert typed.stdout == vm.stdout == "Red Green Red\n9 0\n"


def test_typed_link_rejects_circular_import(tmp_path):
    a_path = tmp_path / "a.ort"
    b_path = tmp_path / "b.ort"
    a_ast = _parse_only('#lang oort-core\nimport "./b"\ndef fa() -> Int { b.fb() }\nprint(fa())\n')
    b_ast = _parse_only('#lang oort-core\nimport "./a"\ndef fb() -> Int { 1 }\n')

    def resolve(spec: str, importer, position):
        if importer == a_path and spec == "./b":
            return b_path, b_ast
        if importer == b_path and spec == "./a":
            return a_path, a_ast
        return None

    with pytest.raises(UnsupportedSyntax, match=r"Circular typed import\."):
        load_typed_units(a_ast, a_path, resolve)


def test_typed_namespace_import_uses_export_table(tmp_path, run_file):
    lib = tmp_path / "lib.ort"
    lib.write_text(LIB_SOURCE, encoding="utf-8")
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nimport "./lib"\nprint(lib.add(2, 3), lib.make_red())\n',
        encoding="utf-8",
    )

    typed = run_file(main, target="tvm")
    assert typed.stdout == "5 Red\n"


def test_typed_module_id_is_relative_to_entry(tmp_path, run_file):
    lib = tmp_path / "lib.ort"
    lib.write_text("#lang oort-core\ndef add(a: Int, b: Int) -> Int { a + b }\n", encoding="utf-8")
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nimport "./lib"\nprint(lib.add(2, 3))\n',
        encoding="utf-8",
    )

    typed = run_file(main, target="tvm")
    assert typed.stdout == "5\n"


def test_typed_collection_obc_round_trip(tmp_path):
    source = """\
#lang oort-core

def first(xs: List[Int]) -> Int { xs[0] }

print(first([4, 5]))
print(len((1, 2, 3)))
"""
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    path = tmp_path / "collections.obc"
    write_typed_obc(program, path)

    loaded = read_typed_obc(path)
    assert loaded.main.types == program.main.types
    assert loaded.main.param_types == program.main.param_types

    result = TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert result.host_value is None


def test_tvm_rejects_out_of_subset():
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises(CompilerError):
        compiler.run_string("#lang oort-core\nclass C { val x: Int = 1 }\nprint(1)\n")


def test_typed_lowering_rejects_out_of_subset():
    ast = build_ast("#lang oort-core\nclass C { val x: Int = 1 }\nprint(1)\n")
    with pytest.raises(UnsupportedSyntax, match="Class definitions"):
        lower_typed_module(ast)


def test_typed_lowering_rejects_top_level_declarations():
    ast = build_ast("#lang oort-core\nval x: Int = 1\nprint(x)\n")
    with pytest.raises(UnsupportedSyntax, match="top-level declarations"):
        lower_typed_module(ast)


def test_typed_lowering_rejects_function_values():
    ast = build_ast(
        """\
#lang oort-core
def f(x: Int) -> Int { x }
val g: (Int) -> Int = f
print(g(1))
"""
    )
    with pytest.raises(UnsupportedSyntax):
        lower_typed_module(ast)
