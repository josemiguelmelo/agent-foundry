from __future__ import annotations

import io
import json
import os
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from agent_foundry.cli import update_check


class TestVersionCompare(unittest.TestCase):
    def test_is_newer_patch(self) -> None:
        self.assertTrue(update_check.is_newer("1.0.1", "1.0.0"))

    def test_is_newer_minor(self) -> None:
        self.assertTrue(update_check.is_newer("1.1.0", "1.0.9"))

    def test_equal_versions(self) -> None:
        self.assertFalse(update_check.is_newer("1.0.0", "1.0.0"))

    def test_older_version(self) -> None:
        self.assertFalse(update_check.is_newer("1.0.0", "1.1.0"))

    def test_strips_v_prefix(self) -> None:
        self.assertTrue(update_check.is_newer("v2.0.0", "1.9.9"))


class TestMaybeEmitUpdateNotice(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_dir = Path(self._testMethodName)
        self.cache_path = self.cache_dir / "update-check.json"

    def tearDown(self) -> None:
        if self.cache_path.is_file():
            self.cache_path.unlink()
        if self.cache_dir.is_dir():
            self.cache_dir.rmdir()

    def _write_cache(
        self,
        *,
        checked_at: str,
        latest: str,
        notified: str = "",
    ) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(
                {
                    "last_checked_at": checked_at,
                    "latest_remote_version": latest,
                    "last_notified_version": notified,
                }
            ),
            encoding="utf-8",
        )

    def test_prints_notice_when_update_available(self) -> None:
        payload = json.dumps({"tag_name": "v1.2.0"}).encode("utf-8")

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, _tb):
                return False

            def read(self):
                return payload

        with (
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            patch("urllib.request.urlopen", return_value=FakeResponse()),
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        output = err.getvalue()
        self.assertIn("1.2.0 is available", output)
        self.assertIn("pipx upgrade agent-foundry", output)

    def test_skips_when_disabled_by_env(self) -> None:
        payload = json.dumps({"tag_name": "v9.9.9"}).encode("utf-8")

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, _tb):
                return False

            def read(self):
                return payload

        with (
            patch.dict(os.environ, {"AGENT_FOUNDRY_NO_UPDATE_CHECK": "1"}),
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            patch("urllib.request.urlopen", return_value=FakeResponse()),
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        self.assertEqual(err.getvalue(), "")

    def test_does_not_renotify_for_same_version(self) -> None:
        fresh = datetime.now(timezone.utc).isoformat()
        self._write_cache(checked_at=fresh, latest="1.2.0", notified="1.2.0")

        with (
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        self.assertEqual(err.getvalue(), "")

    def test_does_not_print_when_installed_is_current(self) -> None:
        payload = json.dumps({"tag_name": "v1.0.0"}).encode("utf-8")

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, _tb):
                return False

            def read(self):
                return payload

        with (
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            patch("urllib.request.urlopen", return_value=FakeResponse()),
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        self.assertEqual(err.getvalue(), "")

    def test_fails_silently_on_network_error(self) -> None:
        with (
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            patch("urllib.request.urlopen", side_effect=OSError("offline")),
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        self.assertEqual(err.getvalue(), "")

    def test_uses_fresh_cache_without_network(self) -> None:
        fresh = datetime.now(timezone.utc).isoformat()
        self._write_cache(checked_at=fresh, latest="1.5.0")

        with (
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            patch("urllib.request.urlopen") as urlopen_mock,
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        urlopen_mock.assert_not_called()
        self.assertIn("1.5.0 is available", err.getvalue())

    def test_refetches_when_cache_is_stale(self) -> None:
        stale = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        self._write_cache(checked_at=stale, latest="1.1.0")
        payload = json.dumps({"tag_name": "v1.3.0"}).encode("utf-8")

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, _tb):
                return False

            def read(self):
                return payload

        with (
            patch.object(update_check, "installed_version", return_value="1.0.0"),
            patch("urllib.request.urlopen", return_value=FakeResponse()) as urlopen_mock,
            redirect_stderr(io.StringIO()) as err,
        ):
            update_check.maybe_emit_update_notice(cache_path=self.cache_path)

        urlopen_mock.assert_called_once()
        self.assertIn("1.3.0 is available", err.getvalue())


if __name__ == "__main__":
    unittest.main()
