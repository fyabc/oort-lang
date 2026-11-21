#! /usr/bin/env python

import logging
import re
import sys
from pathlib import Path

from ..source.input_info import InputInfo
from ..source.source_position import AbstractSourcePosition
from . import OortException, OortSyntaxWarning

logger = logging.getLogger(__name__)


class CompilerErrorHandler:
    def __init__(self):
        self._entries: list[tuple[OortException, InputInfo]] = []
        self._inputs_by_filename: dict[str, InputInfo] = {}
        self._last_input_info: InputInfo | None = None

    @property
    def has_errors(self) -> bool:
        return bool(self._entries)

    @property
    def pending_count(self) -> int:
        """Number of queued diagnostics, including warnings."""
        return len(self._entries)

    @property
    def error_count(self) -> int:
        """Number of queued errors, excluding warnings."""
        return sum(not isinstance(error, OortSyntaxWarning) for error, _ in self._entries)

    def register_input(self, input_info: InputInfo):
        """Remember an input so diagnostics can be paired with their source."""
        self._inputs_by_filename[input_info.input_filename] = input_info
        module_path = input_info.module_path
        if module_path is not None:
            self._inputs_by_filename[str(module_path)] = input_info
        self._last_input_info = input_info

    def input_info_for(self, position: AbstractSourcePosition | None) -> InputInfo | None:
        """Find the input that owns a source position, if it is registered."""
        if position is None:
            return self._last_input_info
        filename = position.filename
        input_info = self._inputs_by_filename.get(filename)
        if input_info is not None:
            return input_info
        # FileStream names are absolute but not resolved; compare resolved
        # paths as well so symlinked or relative entry points still match.
        try:
            resolved = str(Path(filename).resolve())
        except OSError:
            return self._last_input_info
        return self._inputs_by_filename.get(resolved, self._last_input_info)

    def add(self, error: OortException, input_info: InputInfo | None = None):
        if input_info is None:
            input_info = self.input_info_for(error.position)
        if input_info is None:
            raise RuntimeError("Cannot add a diagnostic without source information")
        self._entries.append((error, input_info))

    def clear(self):
        self._entries.clear()

    def retract_since(self, count: int) -> list[tuple[OortException, InputInfo]]:
        """Remove and return the entries added after `count` pending entries.

        Used to replace cascading diagnostics (e.g. parser errors trailing an
        unclosed bracket) with one focused message.
        """
        removed = self._entries[count:]
        del self._entries[count:]
        return removed

    def report(self, exit_on_error: bool = False, clear: bool = True, summary: bool = True) -> int:
        """Report errors.

        Args:
            exit_on_error:
            clear:
            summary:

        Returns:
            Number of errors reported.
        """
        if not self._entries:
            return 0

        entries = sorted(self._entries, key=self._entry_sort_key)

        num_errors, num_warnings = 0, 0
        for error, input_info in entries:
            if isinstance(error, OortSyntaxWarning):
                level = logging.WARNING
                num_warnings += 1
            else:
                level = logging.ERROR
                num_errors += 1
            self._report_position(
                level, type(error).__name__ + ": " + error.msg, error.position, input_info
            )
            for trace_msg, trace_pos in error.traceback:
                trace_input = self.input_info_for(trace_pos) or input_info
                self._report_position(logging.INFO, trace_msg, trace_pos, trace_input)

        if summary and (num_errors > 0 or num_warnings > 0):
            logger.error(f"{num_errors} error{'s' if num_errors != 1 else ''} generated.")
            logger.warning(f"{num_warnings} warning{'s' if num_warnings != 1 else ''} generated.")

        if num_errors > 0 and exit_on_error:
            sys.exit(1)
        if clear:
            self.clear()
        return num_errors

    @staticmethod
    def _entry_sort_key(entry: tuple[OortException, InputInfo]):
        error, input_info = entry
        position = error.position
        if position is None:
            return (input_info.input_filename, 0, 0)
        return (
            position.filename,
            position.start_line,
            position.start_column if position.start_column is not None else 0,
        )

    def _report_position(
        self,
        level: int,
        msg: str,
        position: AbstractSourcePosition | None,
        input_info: InputInfo,
    ):
        if position is None:
            logger.log(level, msg)
            return

        full_msg_lines = [f"{position}: {msg}"]

        lines = input_info.get_lines()
        if position.start_line > len(lines):
            logger.log(level, "\n".join(full_msg_lines))
            return

        # Write start line.
        start_error_line = lines[position.start_line - 1]
        full_msg_lines.append(start_error_line.rstrip("\n"))

        # Write marker line.
        if position.start_column is not None:
            marker_line_prefix = re.sub(
                r"[^\r\n\t]", " ", start_error_line[: position.start_column]
            )
            marker_start = position.start_column
            if position.start_line == position.stop_line and position.stop_column is not None:
                marker_stop = position.stop_column
            else:
                marker_stop = len(start_error_line) - 2  # skip last '\n'
            marker = "^" * max(0, marker_stop - marker_start + 1)
            full_msg_lines.append(f"{marker_line_prefix}{marker}")

        # Write intermediate lines.
        num_intermediate_lines = position.stop_line - position.start_line - 1
        if num_intermediate_lines >= 1:
            full_msg_lines.append(f"... ({num_intermediate_lines} lines) ...\n")

        # Write stop line.
        if num_intermediate_lines >= 0:
            stop_error_line = lines[position.stop_line - 1]
            full_msg_lines.append(stop_error_line)

            # Write stop marker line.
            if position.stop_column is not None and position.stop_column >= 0:
                full_msg_lines.append("^" * (position.stop_column + 1))

        logger.log(level, "\n".join(full_msg_lines))
