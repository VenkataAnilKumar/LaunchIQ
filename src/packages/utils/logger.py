"""Structured logger factory used by all LaunchIQ Python modules."""
from __future__ import annotations

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a logger with a structured formatter, adding a handler only once."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
    return logger
