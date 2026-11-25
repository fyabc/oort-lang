#! /usr/bin/env python

"""Standard diagnostic rendering.

Diagnostics follow the GCC/Clang shape so editors and CI filters can parse the
first line:

    file:line:col: error[Kind]: message
    <source line>
    <caret>

Color is opt-in at call sites and never enabled for non-terminal streams. The
REPL keeps using `rich` for its interactive output; diagnostics do not.
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..source.input_info import InputInfo
    from ..source.source_position import AbstractSourcePosition

_RESET = "\x1b[0m"
_BOLD = "\x1b[1m"
_ERROR = "\x1b[1;31m"
_WARNING = "\x1b[1;33m"
_CARET = "\x1b[1;36m"
_NOTE = "\x1b[1;36m"


def resolve_color(option: str, stream: object) -> bool:
    """Decide whether ANSI color should be emitted.

    Precedence: explicit CLI choice > `NO_COLOR` > `FORCE_COLOR` > tty check.
    `option` is one of `auto`, `always`, `never`.
    """

    if option == "always":
        return True
    if option == "never":
        return False
    if "NO_COLOR" in os.environ:
        return False
    force = os.environ.get("FORCE_COLOR")
    if force is not None and force not in ("", "0"):
        return True
    isatty = getattr(stream, "isatty", None)
    return bool(isatty()) if callable(isatty) else False


def _paint(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def render_diagnostic(
    message: str,
    position: AbstractSourcePosition | None,
    input_info: InputInfo,
    *,
    severity: str = "error",
    kind: str = "",
    color: bool = False,
) -> str:
    """Render one diagnostic as a standard multi-line text block."""

    label = f"{severity}[{kind}]" if kind else severity
    painted_label = _paint(label, _ERROR if severity == "error" else _WARNING, color)
    if position is None:
        head = f"{painted_label}: {message}"
    else:
        head = f"{_paint(str(position), _BOLD, color)}: {painted_label}: {message}"
    return "\n".join([head, *_source_excerpt(position, input_info, color)])


def render_note(
    message: str,
    position: AbstractSourcePosition | None,
    input_info: InputInfo,
    *,
    color: bool = False,
) -> str:
    """Render a secondary note (e.g. a call-site frame)."""

    label = _paint("note", _NOTE, color)
    if position is None:
        return f"  {label}: {message}"
    return f"  {label}: {message} at {position}"


def _source_excerpt(
    position: AbstractSourcePosition | None,
    input_info: InputInfo,
    color: bool,
) -> list[str]:
    """Return the source line(s) and caret marker for a position."""

    if position is None:
        return []

    lines = input_info.get_lines()
    if position.start_line > len(lines):
        return []

    out: list[str] = []
    start_error_line = lines[position.start_line - 1]
    out.append(start_error_line.rstrip("\n"))

    if position.start_column is not None:
        marker_line_prefix = re.sub(r"[^\r\n\t]", " ", start_error_line[: position.start_column])
        marker_start = position.start_column
        if position.start_line == position.stop_line and position.stop_column is not None:
            marker_stop = position.stop_column
        else:
            marker_stop = len(start_error_line) - 2  # skip last '\n'
        marker = "^" * max(0, marker_stop - marker_start + 1)
        out.append(f"{marker_line_prefix}{_paint(marker, _CARET, color)}")

    num_intermediate_lines = position.stop_line - position.start_line - 1
    if num_intermediate_lines >= 1:
        out.append(f"... ({num_intermediate_lines} lines) ...\n")

    if num_intermediate_lines >= 0:
        stop_error_line = lines[position.stop_line - 1]
        out.append(stop_error_line)
        if position.stop_column is not None and position.stop_column >= 0:
            marker = _paint("^" * (position.stop_column + 1), _CARET, color)
            out.append(marker)

    return out
