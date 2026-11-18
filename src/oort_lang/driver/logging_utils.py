#! /usr/bin/env python

import logging
from typing import Any


def setup_logging(level=logging.INFO, rich_logging: bool = True):
    kwargs: dict[str, Any] = {}

    if rich_logging:
        try:
            from rich.logging import RichHandler
            from rich.traceback import install

            install()
        except ImportError:
            pass
        else:
            kwargs["format"] = "%(message)s"
            kwargs["handlers"] = [RichHandler()]

    logging.basicConfig(datefmt="%m/%d %H:%M:%S", level=level, **kwargs)
