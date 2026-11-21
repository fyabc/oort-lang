#! /usr/bin/env python

"""Run every example program as an integration test."""

import re

import pytest

from tests.helpers import EXAMPLES_DIR

EXPECTED_OUTPUTS = {
    "00_basic/00_00_hello_world.ort": "Hello, world!\n",
    "00_basic/00_01_control_flow.ort": "1\n2\n3\n4\n6\n7\n",
    "00_basic/00_02_lang_directive.ort": "oort-object\n",
    "01_functions/01_01_call_with_block.ort": "Before call\nHello, Oort!\nAfter call\nOort!\n",
    "01_functions/01_02_closure.ort": "1\n2\n3\n",
    "01_functions/01_03_parameters.ort": (
        "a.example 80 30 () 2 {:}\n"
        "a.example 443 10 () 2 {:}\n"
        "a.example 443 5 (x, y) 1 {: color: red :}\n"
        "connected\n"
    ),
    "02_collections/02_00_literals.ort": (
        "(1, 2)\n{: a: 1, b: 2 :}\n3 true\n[2, 3]\nello\n[0, 2, 4]\n"
    ),
    "02_collections/02_01_for_loop.ort": ("0\n2\n4\nkey: a\nkey: b\n1 one\n2 two\n1 2 3\n"),
    "03_oop/03_00_inheritance.ort": (
        "rect has area 12\nrect has area 25\n<Type 'Factory'>\n<Type 'M'>\n"
    ),
    "03_oop/03_01_object_model.ort": "1\n0\ntrue\nfalse\nA\n",
    "03_oop/03_02_extensions.ort": (
        "3\n6 6\nmember\nbase child\nnamed person\nabab\nouter inner\n"
    ),
    "04_modules/04_00_imports.ort": "Hello, Oort!\nHello, modules!\n2\n",
    "05_stdlib/05_00_collections.ort": (
        "[6, 2, 4]\n[3, 2]\n[(3, 10), (1, 20)]\n[(0, 3), (1, 1), (2, 2)]\n[1, 2, 3]\n[3, 2, 1]\n"
    ),
    "05_stdlib/05_01_math_string.ort": "3\ntrue\na-b\nOORT\n[a, b, c]\ntrue\n",
    "06_iterators/06_00_user_iterators.ort": ("3\n2\n1\n(a, true) (b, true) (null, false)\n1\n"),
    "08_core/08_00_core_basics.ort": "6\ntrue\ntrue\n",
    "08_core/08_01_core_functions.ort": "1\n120\ntrue\n",
    "08_core/08_02_core_modules.ort": "7\n16\n5\n",
    "08_core/08_03_adt_match.ort": "12\n12\n0\nCircle(1)\n",
    "08_core/08_04_function_values.ort": "6\n15\n",
    "08_core/08_05_currying.ort": "5\n15\n",
    "08_core/08_06_scalars.ort": "2.5\n2 2.0\n1.5\nHello, Oort\ntrue true\n",
    "08_core/08_07_collections_loops.ort": (
        "3 3 0\n7 true 2\n2 2 2\n6\na 1\nb 2\no\no\nr\nt\n1\n3\n"
    ),
    "08_core/08_08_slots.ort": "slot\nctor\n3\norigin\n",
}

# The JSON showcase is covered by `test_json_example.py`, which compiles it
# once and reuses the AST. Running it here as well doubles a ~13s compile.
SEPARATE_EXAMPLES = {"07_showcase/07_00_json.ort"}

EXAMPLE_NAME = re.compile(r"^\d{2}_\d{2}_")
ALL_EXAMPLE_FILES = sorted(
    p.relative_to(EXAMPLES_DIR).as_posix()
    for p in EXAMPLES_DIR.rglob("*.ort")
    if EXAMPLE_NAME.match(p.name)
)
EXAMPLE_FILES = [path for path in ALL_EXAMPLE_FILES if path not in SEPARATE_EXAMPLES]


@pytest.mark.parametrize("rel_path", EXAMPLE_FILES)
def test_example_runs(rel_path: str, run_file):
    result = run_file(EXAMPLES_DIR / rel_path)

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
