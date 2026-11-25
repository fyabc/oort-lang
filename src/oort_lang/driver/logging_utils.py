#! /usr/bin/env python

import logging


def setup_logging(level=logging.INFO):
    """Configure the standard logging sink.

    Diagnostics are rendered by `oort_lang.diagnostics.render` and already
    carry their own layout, so the log format is just the message: no
    timestamps, logger names or level prefixes in CLI output.
    """

    logging.basicConfig(datefmt="%m/%d %H:%M:%S", level=level, format="%(message)s")
