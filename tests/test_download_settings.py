"""Tests for download settings, queue state and media handling."""

from pathlib import Path
import os
import tempfile
import time
import unittest
from unittest.mock import patch

from PyQt6.QtCore import QSettings
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

from zapzap.core.config.settings.downloads import (
    DownloadBehavior,
    DownloadSettings,
    MultipleDownloadPermission,
)
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.features.downloads.download_naming_service import DownloadNamingService
from zapzap.features.downloads.ui.multiple_download_dialog import (
    MultipleDownloadDecision,
)
from zapzap.features.downloads.ui.downloads_menu import DownloadRow


class TemporarySettingsTest(unittest.TestCase):

    def setUp(self):
        self._previous_settings = SettingsManager._settings
        self._temporary_directory = tempfile.TemporaryDirectory()
        settings_path = Path(self._temporary_directory.name) / "settings.ini"
        SettingsManager._settings = QSettings(
            str(settings_path),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        self._temporary_directory.cleanup()


class DownloadSettingsTests(TemporarySettingsTest):

    def test_defaults_preserve_existing_download_dialog(self):
        settings = DownloadSettings()

        self.assertEqual(settings.behavior, DownloadBehavior.DIALOG)
        self.assertFalse(settings.auto_open_pdf)
        self.assertFalse(settings.auto_open_images)

    def test_download_behavior_choices_are_persisted(self):
        settings = DownloadSettings()

        for behavior in (
            DownloadBehavior.DIALOG,
            DownloadBehavior.AUTOMATIC,
            DownloadBehavior.ASK_EVERY_TIME,
        ):
            settings.behavior = behavior
            self.assertEqual(DownloadSettings().behavior, behavior)

    def test_invalid_download_behavior_is_repaired_to_dialog(self):
        SettingsManager.set("downloads/behavior", "invalid")

        self.assertEqual(DownloadSettings().behavior, DownloadBehavior.DIALOG)
        self.assertEqual(
            SettingsManager.get("downloads/behavior"),
            DownloadBehavior.DIALOG,
        )

    def test_pdf_and_image_auto_open_settings_are_independent(self):
        settings = DownloadSettings()
        settings.auto_open_pdf = True
        settings.auto_open_images = False

        reloaded = DownloadSettings()
        self.assertTrue(reloaded.auto_open_pdf)
        self.assertFalse(reloaded.auto_open_images)

    def test_legacy_auto_open_setting_migrates_to_both_switches(self):
        SettingsManager.set("downloads/auto_open_media", True)

        settings = DownloadSettings()

        self.assertTrue(settings.auto_open_pdf)
        self.assertTrue(settings.auto_open_images)
        self.assertFalse(SettingsManager.contains("downloads/auto_open_media"))

    def test_whatsapp_multiple_download_permission_defaults_to_ask(self):
        settings = DownloadSettings()

        self.assertEqual(
            settings.multiple_download_permission,
            MultipleDownloadPermission.ASK,
        )

    def test_whatsapp_multiple_download_permission_can_be_remembered_and_reset(self):
        settings = DownloadSettings()

        settings.multiple_download_permission = (
            MultipleDownloadPermission.ALLOW
        )
        self.assertEqual(
            DownloadSettings().multiple_download_permission,
            MultipleDownloadPermission.ALLOW,
        )

        settings.multiple_download_permission = (
            MultipleDownloadPermission.BLOCK
        )
        self.assertEqual(
            DownloadSettings().multiple_download_permission,
            MultipleDownloadPermission.BLOCK,
        )

        settings.clear_multiple_download_permission()
        self.assertEqual(
            DownloadSettings().multiple_download_permission,
            MultipleDownloadPermission.ASK,
        )


class RepeatedDownloadSecurityTests(TemporarySettingsTest):

    def setUp(self):
        super().setUp()
        self._previous_seen = DownloadManager._has_seen_download_request
        DownloadManager._has_seen_download_request = False

    def tearDown(self):
        DownloadManager._has_seen_download_request = self._previous_seen
        super().tearDown()

    @patch(
        "zapzap.features.downloads.ui.multiple_download_dialog."
        "MultipleDownloadDialog.ask"
    )
    def test_only_first_session_request_is_implicitly_allowed(self, ask):
        ask.return_value = MultipleDownloadDecision.ALLOW_ONCE

        self.assertTrue(DownloadManager._authorize_repeated_download(None))
        ask.assert_not_called()

        self.assertTrue(DownloadManager._authorize_repeated_download(None))
        self.assertEqual(ask.call_count, 1)

        self.assertTrue(DownloadManager._authorize_repeated_download(None))
        self.assertEqual(ask.call_count, 2)

    @patch(
        "zapzap.features.downloads.ui.multiple_download_dialog."
        "MultipleDownloadDialog.ask"
    )
    def test_block_permission_denies_every_later_request(self, ask):
        settings = DownloadSettings()
        settings.multiple_download_permission = MultipleDownloadPermission.BLOCK

        self.assertTrue(DownloadManager._authorize_repeated_download(None))
        self.assertFalse(DownloadManager._authorize_repeated_download(None))
        self.assertFalse(DownloadManager._authorize_repeated_download(None))
        ask.assert_not_called()


class DownloadNamingSecurityTests(unittest.TestCase):

    def test_path_components_are_removed_from_file_name(self):
        self.assertEqual(
            DownloadNamingService.sanitize_file_name("../../report.pdf"),
            "report.pdf",
        )
        self.assertEqual(
            DownloadNamingService.sanitize_file_name(
                r"..\..\report.pdf"
            ),
            "report.pdf",
        )

    def test_control_characters_and_windows_reserved_names_are_sanitized(self):
        self.assertEqual(
            DownloadNamingService.sanitize_file_name("bad\x00name.pdf"),
            "bad_name.pdf",
        )
        self.assertEqual(
            DownloadNamingService.sanitize_file_name("CON.pdf"),
            "_CON.pdf",
        )

    def test_unicode_filename_is_limited_by_utf8_bytes(self):
        original = ("ğ" * 180) + ".pdf"

        safe = DownloadNamingService.sanitize_file_name(original)

        self.assertLessEqual(len(safe.encode("utf-8")), 240)
        self.assertTrue(safe.endswith(".pdf"))

    def test_safe_target_stays_inside_selected_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            safe_directory, safe_name = (
                DownloadNamingService.safe_download_target(
                    directory,
                    "../../report.pdf",
                )
            )

            self.assertEqual(safe_directory, os.path.realpath(directory))
            self.assertEqual(safe_name, "report.pdf")
            self.assertEqual(
                os.path.commonpath(
                    [
                        safe_directory,
                        os.path.realpath(
                            os.path.join(safe_directory, safe_name)
                        ),
                    ]
                ),
                safe_directory,
            )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_existing_symlink_cannot_escape_download_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            with tempfile.TemporaryDirectory() as outside:
                link = os.path.join(directory, "report.pdf")
                try:
                    os.symlink(os.path.join(outside, "outside.pdf"), link)
                except (OSError, NotImplementedError) as error:
                    self.skipTest(
                        f"symlink creation is unavailable: {error}"
                    )

                with self.assertRaises(ValueError):
                    DownloadNamingService.safe_download_target(
                        directory,
                        "report.pdf",
                    )


class FakeDownload:

    def __init__(
        self,
        received,
        total,
        *,
        state=QWebEngineDownloadRequest.DownloadState.DownloadInProgress,
        paused=False,
        name="file.bin",
        directory="/tmp",
        finished=False,
    ):
        self._received = received
        self._total = total
        self._state = state
        self._paused = paused
        self._name = name
        self._directory = directory
        self._finished = finished
        self._cancelled = False

    def state(self):
        return self._state

    def isPaused(self):
        return self._paused

    def isFinished(self):
        return self._finished

    def receivedBytes(self):
        return self._received

    def totalBytes(self):
        return self._total

    def downloadDirectory(self):
        return self._directory

    def downloadFileName(self):
        return self._name

    def suggestedFileName(self):
        return self._name

    def interruptReasonString(self):
        return ""

    def cancel(self):
        self._cancelled = True
        self._state = QWebEngineDownloadRequest.DownloadState.DownloadCancelled


class DownloadQueueTests(unittest.TestCase):

    def setUp(self):
        self._previous_active = DownloadManager._active_downloads
        self._previous_queued = DownloadManager._queued_downloads
        self._previous_meta = DownloadManager._download_meta
        self._previous_terminal = DownloadManager._terminal_records

        DownloadManager._active_downloads = []
        DownloadManager._queued_downloads = []
        DownloadManager._download_meta = {}
        DownloadManager._terminal_records = []

    def tearDown(self):
        DownloadManager._active_downloads = self._previous_active
        DownloadManager._queued_downloads = self._previous_queued
        DownloadManager._download_meta = self._previous_meta
        DownloadManager._terminal_records = self._previous_terminal

    def track(self, download, sequence=1):
        DownloadManager._active_downloads.append(download)
        DownloadManager._download_meta[id(download)] = {
            "sequence": sequence,
            "status": "active",
            "open_on_complete": False,
            "terminal_override": None,
        }

    def test_progress_is_weighted_by_total_bytes(self):
        first = FakeDownload(50, 100, name="first.bin")
        second = FakeDownload(100, 300, name="second.bin")
        self.track(first, sequence=1)
        self.track(second, sequence=2)

        self.assertEqual(DownloadManager.progress_summary(), (2, 38))

    def test_unknown_size_returns_no_percentage(self):
        download = FakeDownload(10, -1)
        self.track(download)

        self.assertEqual(DownloadManager.progress_summary(), (1, None))

    def test_no_active_downloads_returns_empty_summary(self):
        self.assertEqual(DownloadManager.progress_summary(), (0, None))

    def test_whatsapp_active_limit_is_global(self):
        self.assertEqual(DownloadManager.MAX_ACTIVE_DOWNLOADS, 6)

        for index in range(6):
            self.track(
                FakeDownload(0, 100, name=f"file-{index}.bin"),
                sequence=index,
            )

        self.assertEqual(DownloadManager._active_download_count(), 6)

    def test_paused_download_does_not_use_an_active_slot(self):
        for index in range(5):
            self.track(
                FakeDownload(0, 100, name=f"file-{index}.bin"),
                sequence=index,
            )

        self.track(
            FakeDownload(
                0,
                100,
                paused=True,
                name="paused.bin",
            ),
            sequence=10,
        )

        self.assertEqual(DownloadManager._active_download_count(), 5)

    def test_dismissed_unstarted_download_is_not_recorded(self):
        download = FakeDownload(
            0,
            100,
            state=QWebEngineDownloadRequest.DownloadState.DownloadRequested,
            name="dismissed.pdf",
        )
        self.track(download, sequence=1)

        DownloadManager._discard_unstarted_download(download)
        DownloadManager._handle_state(
            download,
            QWebEngineDownloadRequest.DownloadState.DownloadCancelled,
        )

        self.assertEqual(DownloadManager._terminal_records, [])
        self.assertNotIn(download, DownloadManager._active_downloads)

    def test_terminal_state_keeps_original_sequence_position(self):
        older = FakeDownload(10, 100, name="older.bin")
        newer = FakeDownload(20, 100, name="newer.bin")
        self.track(older, sequence=1)
        self.track(newer, sequence=2)

        DownloadManager._record_terminal(older, "cancelled")
        DownloadManager._release_download(older)

        items = DownloadManager.download_items()
        self.assertEqual(items[0]["name"], "newer.bin")
        self.assertEqual(items[1]["name"], "older.bin")
        self.assertEqual(items[1]["status"], "cancelled")

    def test_progress_percent_badge_waits_for_large_slow_download(self):
        download = FakeDownload(
            5 * 1024 * 1024,
            20 * 1024 * 1024,
            name="large.bin",
        )
        self.track(download, sequence=1)
        DownloadManager._download_meta[id(download)]["started_at"] = (
            time.monotonic() - 6
        )

        count, percent, show_percent = DownloadManager.progress_indicator()

        self.assertEqual(count, 1)
        self.assertEqual(percent, 25)
        self.assertTrue(show_percent)

    def test_progress_percent_badge_stays_hidden_for_small_or_fast_download(self):
        small = FakeDownload(
            1 * 1024 * 1024,
            5 * 1024 * 1024,
            name="small.bin",
        )
        self.track(small, sequence=1)
        DownloadManager._download_meta[id(small)]["started_at"] = (
            time.monotonic() - 10
        )
        self.assertEqual(
            DownloadManager.progress_indicator(),
            (1, 20, False),
        )

        DownloadManager._active_downloads = []
        DownloadManager._download_meta = {}

        fast = FakeDownload(
            5 * 1024 * 1024,
            20 * 1024 * 1024,
            name="fast.bin",
        )
        self.track(fast, sequence=2)
        DownloadManager._download_meta[id(fast)]["started_at"] = (
            time.monotonic() - 1
        )
        self.assertEqual(
            DownloadManager.progress_indicator(),
            (1, 25, False),
        )

    def test_queued_item_is_exposed_as_queued(self):
        queued = FakeDownload(
            0,
            100,
            state=QWebEngineDownloadRequest.DownloadState.DownloadRequested,
            name="queued.pdf",
        )
        self.track(queued)
        DownloadManager._queued_downloads.append(queued)

        item = DownloadManager.item_snapshot(id(queued))

        self.assertIsNotNone(item)
        self.assertEqual(item["status"], "queued")
        self.assertEqual(item["percent"], 0)


class DownloadMenuPresentationTests(unittest.TestCase):

    class _FakeIcon:
        def __init__(self, key):
            self.key = key

        def isNull(self):
            return False

        def cacheKey(self):
            return self.key

    class _FakeProvider:
        def __init__(self):
            self.type_icon = DownloadMenuPresentationTests._FakeIcon(2)
            self.generic_icon = DownloadMenuPresentationTests._FakeIcon(1)

        def icon(self, value):
            if hasattr(value, "fileName"):
                return self.type_icon
            return self.generic_icon

    def test_native_file_type_icon_is_preferred_for_missing_target(self):
        previous = DownloadRow._file_icon_provider
        provider = self._FakeProvider()
        DownloadRow._file_icon_provider = provider
        try:
            icon = DownloadRow._system_file_icon("", "report.pdf")
        finally:
            DownloadRow._file_icon_provider = previous

        self.assertIs(icon, provider.type_icon)

    def test_long_name_is_middle_elided_and_keeps_extension(self):
        name = (
            "denemedosyasi-cok-uzun-bir-dosya-adi-"
            "ve-devami-burada.pdf"
        )

        rendered = DownloadRow._elide_file_name(name, 38)

        self.assertLessEqual(len(rendered), 38)
        self.assertIn("…", rendered)
        self.assertTrue(rendered.endswith(".pdf"))
        self.assertTrue(rendered.startswith("deneme"))


class DownloadAutoOpenTypeTests(unittest.TestCase):

    def _write_file(self, suffix, payload):
        temporary = tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        )
        try:
            temporary.write(payload)
            temporary.close()
            return temporary.name
        except Exception:
            temporary.close()
            os.unlink(temporary.name)
            raise

    def test_verified_pdf_can_auto_open(self):
        path = self._write_file(
            ".pdf",
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n",
        )
        try:
            self.assertTrue(
                DownloadManager.supports_auto_open(
                    "application/pdf",
                    os.path.basename(path),
                    path,
                )
            )
            self.assertEqual(
                DownloadManager.auto_open_kind(
                    "application/pdf",
                    os.path.basename(path),
                    path,
                ),
                "pdf",
            )
        finally:
            os.unlink(path)

    def test_verified_png_can_auto_open(self):
        path = self._write_file(
            ".png",
            b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32),
        )
        try:
            self.assertTrue(
                DownloadManager.supports_auto_open(
                    "image/png",
                    os.path.basename(path),
                    path,
                )
            )
            self.assertEqual(
                DownloadManager.auto_open_kind(
                    "image/png",
                    os.path.basename(path),
                    path,
                ),
                "image",
            )
        finally:
            os.unlink(path)

    def test_safe_content_with_dangerous_extension_is_not_auto_opened(self):
        path = self._write_file(
            ".exe",
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n",
        )
        try:
            self.assertFalse(
                DownloadManager.supports_auto_open(
                    "application/pdf",
                    os.path.basename(path),
                    path,
                )
            )
        finally:
            os.unlink(path)

    def test_conflicting_reported_mime_is_not_auto_opened(self):
        path = self._write_file(
            ".pdf",
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n",
        )
        try:
            self.assertFalse(
                DownloadManager.supports_auto_open(
                    "application/x-msdownload",
                    os.path.basename(path),
                    path,
                )
            )
        finally:
            os.unlink(path)

    def test_svg_is_not_in_automatic_open_allowlist(self):
        path = self._write_file(
            ".svg",
            b'<svg xmlns="http://www.w3.org/2000/svg"></svg>',
        )
        try:
            self.assertFalse(
                DownloadManager.supports_auto_open(
                    "image/svg+xml",
                    os.path.basename(path),
                    path,
                )
            )
        finally:
            os.unlink(path)

    def test_non_media_file_is_not_auto_opened(self):
        path = self._write_file(".txt", b"hello")
        try:
            self.assertFalse(
                DownloadManager.supports_auto_open(
                    "text/plain",
                    os.path.basename(path),
                    path,
                )
            )
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
