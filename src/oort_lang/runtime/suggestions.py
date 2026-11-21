#! /usr/bin/env python

"""Python-habit suggestions appended to name and operator error messages.

Counterparts of Python's "did you mean" hints: the name table covers the
built-ins Python spells differently, the operator table covers boolean
operators Python spells with symbols. Shared by the tree-walking
interpreter and the bytecode VM (which delegates operator dispatch).
"""

from __future__ import annotations

_NAME_SUGGESTIONS = {
    "None": "null",
    "True": "true",
    "False": "false",
    "self": "this",
}

_OPERATOR_SUGGESTIONS = {
    "&&": "and",
    "||": "or",
    "!": "not",
}


def name_suggestion(name: str) -> str:
    """Suffix suggesting the Oort spelling of a Python built-in name."""
    suggested = _NAME_SUGGESTIONS.get(name)
    return "" if suggested is None else f" (did you mean {suggested!r}?)"


def operator_suggestion(symbol: str) -> str:
    """Suffix suggesting the Oort spelling of a Python operator."""
    suggested = _OPERATOR_SUGGESTIONS.get(symbol)
    return "" if suggested is None else f" (did you mean {suggested!r}?)"
