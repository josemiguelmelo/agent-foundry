"""Passive check for newer agent-foundry releases on GitHub."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from agent_foundry.utils.json_io import read_json_dict_or_default, write_json

_PACKAGE_NAME = "agent-foundry"
_GITHUB_API_URL = (
    "https://api.github.com/repos/josemiguelmelo/agent-foundry/releases/latest"
)
_RELEASES_URL = "https://github.com/josemiguelmelo/agent-foundry/releases"
_DISABLE_ENV = "AGENT_FOUNDRY_NO_UPDATE_CHECK"
_CHECK_INTERVAL_SECONDS = 24 * 60 * 60
_CACHE_PATH = Path.home() / ".agent-foundry" / "update-check.json"
_USER_AGENT = "agent-foundry-cli"


def installed_version() -> str:
    try:
        return version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0"


def version_tuple(raw: str) -> tuple[int, ...]:
    """Parse a semver prefix into comparable integer tuple."""
    cleaned = raw.strip().lstrip("v").split("-", 1)[0]
    parts: list[int] = []
    for piece in cleaned.split("."):
        if not piece.isdigit():
            break
        parts.append(int(piece))
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    return version_tuple(latest) > version_tuple(current)


def fetch_latest_release_version() -> str | None:
    request = urllib.request.Request(
        _GITHUB_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": _USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        OSError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return None

    tag_name = payload.get("tag_name")
    if not isinstance(tag_name, str) or not tag_name:
        return None
    return tag_name.lstrip("v")


def _parse_checked_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _cache_is_fresh(checked_at: datetime | None) -> bool:
    if checked_at is None:
        return False
    age = datetime.now(timezone.utc) - checked_at.astimezone(timezone.utc)
    return age.total_seconds() < _CHECK_INTERVAL_SECONDS


def maybe_emit_update_notice(*, cache_path: Path = _CACHE_PATH) -> None:
    if os.environ.get(_DISABLE_ENV) == "1":
        return

    installed = installed_version()
    cache = read_json_dict_or_default(
        cache_path,
        {
            "last_checked_at": "",
            "latest_remote_version": "",
            "last_notified_version": "",
        },
    )

    checked_at = _parse_checked_at(cache.get("last_checked_at"))
    latest = cache.get("latest_remote_version")
    if not isinstance(latest, str):
        latest = ""

    if _cache_is_fresh(checked_at) and latest:
        remote_version = latest
    else:
        remote_version = fetch_latest_release_version()
        if remote_version:
            cache["last_checked_at"] = datetime.now(timezone.utc).isoformat()
            cache["latest_remote_version"] = remote_version
            write_json(cache_path, cache)
        elif latest:
            remote_version = latest
        else:
            return

    if not is_newer(remote_version, installed):
        return

    last_notified = cache.get("last_notified_version")
    if isinstance(last_notified, str) and last_notified == remote_version:
        return

    print(
        f"agent-foundry {remote_version} is available (installed {installed}). "
        "Upgrade: pipx upgrade agent-foundry",
        file=sys.stderr,
    )
    print(f"See {_RELEASES_URL}", file=sys.stderr)

    cache["last_notified_version"] = remote_version
    write_json(cache_path, cache)
