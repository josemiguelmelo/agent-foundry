"""Markdown/frontmatter rewrites used by Cursor CLI mirror."""

from __future__ import annotations

from pathlib import Path

from agent_foundry.utils.markdown import (
    assemble_frontmatter_markdown,
    split_frontmatter_for_rewrite,
)

FRONTMATTER_PLUGIN_KEY = "x-agent-foundry-plugin"


def iter_skill_package_dirs(skills_ref: Path) -> list[Path]:
    """Directories that contain SKILL.md (either the ref itself or its subfolders)."""
    if not skills_ref.exists():
        return []
    if skills_ref.is_dir() and (skills_ref / "SKILL.md").is_file():
        return [skills_ref]
    if not skills_ref.is_dir():
        return []
    found: list[Path] = []
    for child in sorted(skills_ref.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            found.append(child)
    return found


def iter_agent_sources(agents_ref: Path) -> list[Path]:
    """Markdown agent files under agents path."""
    if agents_ref.is_file() and agents_ref.suffix.lower() == ".md":
        return [agents_ref]
    if agents_ref.is_dir():
        return sorted(p for p in agents_ref.glob("*.md") if p.is_file())
    return []


def rewrite_agent_for_cli(plugin_id: str, src_md: Path) -> str:
    raw = src_md.read_text(encoding="utf-8")
    fm, body = split_frontmatter_for_rewrite(raw)
    stem = src_md.stem
    prefixed_name = f"{plugin_id}__{stem}"
    fm["name"] = prefixed_name
    fm[FRONTMATTER_PLUGIN_KEY] = plugin_id
    return assemble_frontmatter_markdown(fm, body)
