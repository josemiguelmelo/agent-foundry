"""Path helpers for provider install scopes."""

from __future__ import annotations

from pathlib import Path


def install_base(*, in_project: bool) -> Path:
    """User home vs current working directory for global vs project-scoped installs."""
    return Path.cwd().resolve() if in_project else Path.home()


def resolve_under(root: Path, raw: str) -> Path:
    """Interpret ``raw`` relative to ``root`` when not absolute."""
    p = Path(raw.strip())
    if not p.is_absolute():
        p = root / p
    return p.resolve()
