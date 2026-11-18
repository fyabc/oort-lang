#! /usr/bin/env python

"""Run every example program as an integration test."""

import pytest

from tests.helpers import EXAMPLES_DIR

EXPECTED_OUTPUTS = {
    "00_basic/00_00_hello_world.ort": "Hello, world!\n",
    "00_basic/00_01_control_flow.ort": "1\n2\n3\n4\n6\n7\n",
    "00_basic/00_02_lang_directive.ort": "oort-object\n",
    "01_functions/01_01_call_with_block.ort": "Before call\nHello, Oort!\nAfter call\nOort!\n",
    "01_functions/01_02_closure.ort": "1\n2\n3\n",
    "02_collections/02_00_literals.ort": (
        "(1, 2)\n{: a: 1, b: 2 :}\n3 true\n[2, 3]\nello\n[0, 2, 4]\n"
    ),
    "02_collections/02_01_for_loop.ort": ("0\n2\n4\nkey: a\nkey: b\n1 one\n2 two\n1 2 3\n"),
    "03_oop/03_00_inheritance.ort": (
        "rect has area 12\nrect has area 25\n<Type 'Factory'>\n<Type 'M'>\n"
    ),
    "03_oop/03_01_object_model.ort": "1\n0\ntrue\nfalse\nA\n",
}

EXAMPLE_FILES = sorted(p.relative_to(EXAMPLES_DIR).as_posix() for p in EXAMPLES_DIR.rglob("*.ort"))


@pytest.mark.parametrize("rel_path", EXAMPLE_FILES)
def test_example_runs(rel_path: str, run_source):
    code = (EXAMPLES_DIR / rel_path).read_text(encoding="utf-8")
    result = run_source(code)

    if rel_path == "01_functions/01_00_fibonacci.ort":
        # The elapsed time is non-deterministic; check the result only.
        assert result.stdout.startswith("Time elapsed:")
        assert result.stdout.endswith("6765\n")
    else:
        assert result.stdout == EXPECTED_OUTPUTS[rel_path]


def test_all_examples_have_expected_output():
    missing = [path for path in EXAMPLE_FILES if path not in EXPECTED_OUTPUTS]
    missing = [path for path in missing if path != "01_functions/01_00_fibonacci.ort"]
    assert not missing, f"Examples without expected output: {missing}"
