#! /usr/bin/env python

"""Helpers for reserved names."""

import re

ANONYMOUS_PARAMETER_RE = re.compile(r"\$(\d*)")


def anonymous_param_index(name: str) -> int | None:
    """Return the index of an anonymous parameter name (`$0`, `$1`, ...)."""
    match = ANONYMOUS_PARAMETER_RE.fullmatch(name)
    if match is None:
        return None
    digits = match.group(1)
    return int(digits) if digits else 0
