#! /usr/bin/env python

import logging
import re
import sys

from ..exceptions import OortException, OortSyntaxWarning
from ..support.input_info import InputInfo
from ..support.source_position import AbstractSourcePosition

logger = logging.getLogger(__name__)


class CompilerErrorHandler:
    def __init__(self):
        self.errors: list[OortException] = []
        self.input_infos = []

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def add(self, error: OortException, input_info: InputInfo):
        self.errors.append(error)
        self.input_infos.append(input_info)

    def clear(self):
        self.errors.clear()
        self.input_infos.clear()

    def report(self, exit_on_error: bool = False, clear: bool = True, summary: bool = True) -> int:
        """Report errors.

        Args:
            exit_on_error:
            clear:
            summary:

        Returns:
            Number of errors reported.
        """
        if not self.errors:
            return 0

        self.errors.sort(key=lambda x: x.position.sort_key)

        num_errors, num_warnings = 0, 0
        for error, input_info in zip(self.errors, self.input_infos, strict=False):
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
                self._report_position(logging.INFO, trace_msg, trace_pos, input_info)

        if summary and (num_errors > 0 or num_warnings > 0):
            logger.error(f"{num_errors} error{'s' if num_errors != 1 else ''} generated.")
            logger.warning(f"{num_warnings} warning{'s' if num_warnings != 1 else ''} generated.")

        if num_errors > 0 and exit_on_error:
            sys.exit(1)
        if clear:
            self.clear()
        return num_errors

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
