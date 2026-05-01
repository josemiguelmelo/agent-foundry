"""Shared helpers for provider install/uninstall."""

from __future__ import annotations

import shutil
from pathlib import Path


def which_cmd(cmd: str) -> str | None:
    return shutil.which(cmd)


def replace_copytree(src: Path, dst: Path) -> None:
    """Copy plugin tree into ``dst`` (remove existing file, symlink, or directory first)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    shutil.copytree(src.resolve(), dst, symlinks=True)
