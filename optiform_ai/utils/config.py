"""Lightweight configuration loader."""
from __future__ import annotations

from dataclasses import dataclass
import os


def _get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


@dataclass
class Settings:
    log_level: str = _get_env("OPTIFORM_LOG_LEVEL", "INFO")
    data_path: str | None = _get_env("OPTIFORM_DATA_PATH")

    @classmethod
    def load(cls) -> "Settings":
        return cls()
