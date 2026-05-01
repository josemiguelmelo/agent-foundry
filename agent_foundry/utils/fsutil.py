"""Filesystem helpers."""

from __future__ import annotations

import shutil
from pathlib import Path


def unlink_or_rmtree(target: Path) -> bool:
    """
    Remove a symlink, file, or directory tree.
    Returns True if something was removed.
    """
    if not target.exists() and not target.is_symlink():
        return False
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
    else:
        target.unlink()
    return True


def prune_empty_parents(from_dir: Path, *, stop_at: Path) -> None:
    """
    Remove ``from_dir`` and then parent directories while each is empty.
    Stops at ``stop_at`` (that directory is never removed).
    """
    stop_at = stop_at.resolve()
    cur = from_dir.resolve()
    while cur != stop_at:
        try:
            if not cur.is_dir():
                break
            if any(cur.iterdir()):
                break
            parent = cur.parent
            cur.rmdir()
            cur = parent
        except OSError:
            break
