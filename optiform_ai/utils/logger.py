"""Project-wide logging helper."""
from __future__ import annotations

import logging
from functools import lru_cache
from .config import Settings


@lru_cache(maxsize=1)
def get_logger(name: str = "optiform_ai") -> logging.Logger:
    settings = Settings.load()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    return logging.getLogger(name)
