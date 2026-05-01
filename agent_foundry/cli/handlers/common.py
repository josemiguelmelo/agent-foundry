"""Shared helpers for CLI command handlers."""

from __future__ import annotations

import sys
from typing import Callable


def run_with_errors(
    fn: Callable[[], int],
    mapping: dict[type[Exception], int],
) -> int:
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        for exc_type, code in mapping.items():
            if isinstance(e, exc_type):
                print(e, file=sys.stderr)
                return code
        raise
