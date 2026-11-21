#! /usr/bin/env python

"""Differential error tests between the tree-walking interpreter and the VM.

The same failing program must fail the same way under both backends. Each
corpus entry declares how strictly the two diagnostics must agree:

- ``strict``: diagnostic type, message and line number must match exactly;
- ``text``: diagnostic type and message must match; the line number may
  differ where the VM reports the enclosing expression (whole binary
  expression / whole ``for`` expression) instead of a sub-expression token;
- ``both_fail``: both backends must reject the program; the VM rejects some
  constructs at lowering time that the interpreter only rejects at runtime,
  so only the failure itself is compared;
- ``vm_rejects``: the interpreter runs the program but the VM rejects it at
  the HIR subset boundary; the expected VM message is asserted.
"""

import logging
import re

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler

# Diagnostic first line: "{filename}:{line}:{column}: {Type}: {message}".
# The filename may itself contain colons (Windows drive letters), so the
# location is split from the right. The kind is not always ``Oort*``:
# lowering rejections report ``UnsupportedSyntax`` and static checks report
# ``TypeCheckError``.
_DIAGNOSTIC = re.compile(r"^(?P<location>.*): (?P<kind>[A-Z]\w*): (?P<message>.*)$")


def _split_location(location: str) -> int | None:
    """Return the line number from "filename:line[:column]", if present."""
    parts = location.rsplit(":", 2)
    if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
        return int(parts[1])
    parts = location.rsplit(":", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return int(parts[1])
    return None


STRICT = "strict"
TEXT = "text"
BOTH_FAIL = "both_fail"
VM_REJECTS = "vm_rejects"

CORPUS = [
    # --- Name resolution -------------------------------------------------
    pytest.param("print(missing)\n", STRICT, id="unbound-global"),
    pytest.param("def f() { print(missing) }\nf()\n", STRICT, id="unbound-in-function"),
    pytest.param("x += 1\n", STRICT, id="aug-assign-unbound"),
    # --- Operators and arithmetic ----------------------------------------
    pytest.param('print(1 + "a")\n', STRICT, id="operator-type-mismatch"),
    pytest.param(
        'val x = 1\nprint(x\n   + "a")\n',
        TEXT,
        id="operator-multiline-position",
    ),
    pytest.param("print(1 / 0)\n", STRICT, id="division-by-zero"),
    pytest.param("print(1 // 0)\n", STRICT, id="floor-division-by-zero"),
    pytest.param("print(1 % 0)\n", STRICT, id="modulo-by-zero"),
    # --- Attributes and subscripts (shared implementations) --------------
    pytest.param("print([1].missing)\n", STRICT, id="missing-attribute"),
    pytest.param("val xs = [1]\nxs.foo = 1\n", STRICT, id="set-attribute-on-native"),
    pytest.param("val t = (1, 2)\nt[0] = 3\n", STRICT, id="item-assignment-on-tuple"),
    pytest.param(
        'val d = {: "a": 1 :}\nprint(d["b"])\n',
        STRICT,
        id="dict-missing-key",
    ),
    # --- Calls and parameter binding --------------------------------------
    pytest.param("val x = 1\nx()\n", STRICT, id="not-callable"),
    pytest.param("val x = 1\nx(a = 1)\n", STRICT, id="not-callable-keyword"),
    pytest.param("print(value = 1)\n", STRICT, id="builtin-keyword"),
    pytest.param("def f(a, b) { a }\nf(1)\n", STRICT, id="missing-required"),
    pytest.param("def f(a) { a }\nf(1, a = 2)\n", STRICT, id="multiple-values"),
    pytest.param("def f(a, /) { a }\nf(a = 1)\n", STRICT, id="positional-only"),
    pytest.param("def f(*, a) { a }\nf()\n", STRICT, id="keyword-only-missing"),
    pytest.param("def f(a) { a }\nf(b = 1)\n", STRICT, id="unexpected-keyword"),
    # --- Classes -----------------------------------------------------------
    pytest.param("class C {}\nC(1)\n", STRICT, id="class-arity-without-init"),
    pytest.param(
        "class C { def __init__(x) { this.x = x } }\nC()\n",
        STRICT,
        id="class-init-missing-required",
    ),
    pytest.param(
        "class C {}\nprint(C().missing)\n",
        STRICT,
        id="instance-missing-attribute",
    ),
    # --- Iterator protocol (shared implementations) ------------------------
    pytest.param("class C {}\nfor x in C() { print(x) }\n", STRICT, id="not-iterable"),
    pytest.param(
        "class C { def __iter__() { 1 } }\nfor x in C() { print(x) }\n",
        STRICT,
        id="iter-returns-non-callable",
    ),
    pytest.param(
        "class C { def __iter__() { do: 1 } }\nfor x in C() { print(x) }\n",
        STRICT,
        id="iterator-returns-non-tuple",
    ),
    pytest.param("for a, b in [1] { print(a) }\n", STRICT, id="loop-unpack-non-tuple"),
    pytest.param(
        "for a, b in [(1, 2, 3)] { print(a) }\n",
        STRICT,
        id="loop-unpack-arity",
    ),
    # --- Extensions ---------------------------------------------------------
    pytest.param(
        "var not_a_type = 1\ndef not_a_type.f: 1\n",
        STRICT,
        id="extension-receiver-not-a-type",
    ),
    pytest.param(
        'var not_a_type = 1\ndef not_a_type.operator "+"(other) { 1 }\n',
        STRICT,
        id="extension-operator-receiver-not-a-type",
    ),
    pytest.param(
        "class C {}\ndef g() { def C.f: 1\n def C.f: 2 }\ng()\n",
        STRICT,
        id="duplicate-extension-method",
    ),
    pytest.param(
        "class C {}\n"
        'def g() { def C.operator "+"(other) { 1 }\n'
        ' def C.operator "+"(other) { 2 } }\n'
        "g()\n",
        STRICT,
        id="duplicate-extension-operator",
    ),
    # --- Timing differences: interpreter runtime error vs HIR rejection ----
    pytest.param("val x = 1\nx = 2\n", BOTH_FAIL, id="assign-immutable"),
    pytest.param("super.__init__()\n", BOTH_FAIL, id="super-outside-method"),
    pytest.param("var x\n", BOTH_FAIL, id="declaration-without-initializer"),
    pytest.param("a, b = 1, 2\n", BOTH_FAIL, id="tuple-assignment"),
    # --- Explicit HIR subset boundary: interpreter runs, VM rejects ---------
    pytest.param("...\n", VM_REJECTS, id="ellipsis"),
]


def _diagnostics(caplog: pytest.LogCaptureFixture) -> list[tuple[str, str, int | None]]:
    """Extract ``(type, message, line)`` from reported ERROR diagnostics."""
    results = []
    for record in caplog.records:
        if record.levelno != logging.ERROR:
            continue
        first_line = record.getMessage().splitlines()[0]
        match = _DIAGNOSTIC.match(first_line)
        if match is None:
            continue  # summary line ("N errors generated.")
        results.append(
            (
                match.group("kind"),
                match.group("message"),
                _split_location(match.group("location")),
            )
        )
    return results


def _run_failing(target: str, source: str, caplog: pytest.LogCaptureFixture):
    """Run `source`, which must be rejected; return its diagnostics.

    Rejection covers both runtime failures (`CompilerError`) and
    compile-stage diagnostics (`SystemExit` via the error handler).
    """
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    caplog.clear()
    with pytest.raises((CompilerError, SystemExit)):
        compiler.run_string(source)
    return _diagnostics(caplog)


@pytest.mark.parametrize(("source", "mode"), CORPUS)
def test_error_matches_interpreter(
    source: str,
    mode: str,
    caplog: pytest.LogCaptureFixture,
):
    if mode == VM_REJECTS:
        eval_compiler = get_compiler(["NOT_EXIST", "-t", "eval"])
        eval_compiler.run_string(source)  # must run under the interpreter
        caplog.clear()
        vm_compiler = get_compiler(["NOT_EXIST", "-t", "vm"])
        with pytest.raises((CompilerError, SystemExit)):
            vm_compiler.run_string(source)
        vm_diagnostic = _diagnostics(caplog)
        assert vm_diagnostic, "VM rejection must report a diagnostic"
        assert "HIR backend does not support" in vm_diagnostic[0][1]
        return

    if mode == BOTH_FAIL:
        eval_diagnostic = _run_failing("eval", source, caplog)
        vm_diagnostic = _run_failing("vm", source, caplog)
        assert eval_diagnostic, "interpreter must reject the program"
        assert vm_diagnostic, "VM must reject the program"
        return

    eval_diagnostic = _run_failing("eval", source, caplog)
    vm_diagnostic = _run_failing("vm", source, caplog)
    assert eval_diagnostic, "interpreter must report at least one error"
    assert vm_diagnostic, "VM must report at least one error"

    eval_kind, eval_message, eval_line = eval_diagnostic[0]
    vm_kind, vm_message, vm_line = vm_diagnostic[0]

    assert vm_kind == eval_kind
    assert vm_message == eval_message
    if mode == STRICT:
        assert vm_line == eval_line


def test_error_diff_import_failures(tmp_path, run_file, caplog: pytest.LogCaptureFixture):
    """Import errors flow through the shared ModuleLoader on both backends."""
    main = tmp_path / "main.ort"
    main.write_text('import "./nope"\n', encoding="utf-8")

    for target in ("eval", "vm"):
        caplog.clear()
        with pytest.raises(CompilerError):
            run_file(main, target=target)
        diagnostic = _diagnostics(caplog)
        assert diagnostic
        kind, message, line = diagnostic[0]
        assert kind == "OortImportError"
        assert message.startswith("Cannot find module './nope'.")
        assert line == 1
