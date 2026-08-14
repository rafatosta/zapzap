"""Regression tests for persisted values passed to narrow Qt integer APIs."""

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from PyQt6.QtCore import QByteArray, QSettings

from zapzap.app.window_lifecycle import WindowLifecycle
from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.config.settings.window import WindowSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.proxy_manager import ProxyManager
from zapzap.features.accounts.domain.user import (
    DEFAULT_ZOOM_FACTOR,
    MAX_ZOOM_FACTOR,
    MIN_ZOOM_FACTOR,
    User,
    apply_zoom_factor,
)
from zapzap.features.downloads.download_manager import DownloadManager


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


class AppearanceFallbackTests(TemporarySettingsTest):

    def test_corrupt_scale_and_tray_theme_are_repaired(self):
        SettingsManager.set("system/scale", "invalid")
        SettingsManager.set("system/tray_theme", "unknown")

        with self.assertLogs(
            "zapzap.core.config.settings.appearance",
            level="WARNING",
        ):
            settings = AppearanceSettings()
            self.assertEqual(settings.scale, 100)
            self.assertEqual(settings.tray_theme, TrayIcon.Type.Default.value)

        self.assertEqual(SettingsManager.get("system/scale"), 100)
        self.assertEqual(
            SettingsManager.get("system/tray_theme"),
            TrayIcon.Type.Default.value,
        )


class WindowStateFallbackTests(TemporarySettingsTest):

    def test_wrong_types_are_replaced_with_empty_byte_arrays(self):
        SettingsManager.set("main/geometry", "not-a-byte-array")
        SettingsManager.set("main/windowState", 42)

        with self.assertLogs(
            "zapzap.core.config.settings.window",
            level="WARNING",
        ):
            settings = WindowSettings()
            self.assertTrue(settings.geometry.isEmpty())
            self.assertTrue(settings.layout_state.isEmpty())

        self.assertIsInstance(SettingsManager.get("main/geometry"), QByteArray)
        self.assertIsInstance(SettingsManager.get("main/windowState"), QByteArray)

    def test_qt_rejection_discards_only_the_invalid_saved_state(self):
        settings = WindowSettings()
        settings.geometry = QByteArray(b"bad-geometry")
        settings.layout_state = QByteArray(b"bad-layout")
        host = Mock()
        host.restoreGeometry.return_value = False
        content = Mock()
        content.restoreState.side_effect = RuntimeError("simulated Qt failure")
        lifecycle = WindowLifecycle(host, content)

        with (
            patch(
                "zapzap.app.window_lifecycle.SysTrayManager.start"
            ) as start_tray,
            self.assertLogs(
                "zapzap.app.window_lifecycle",
                level="ERROR",
            ),
        ):
            lifecycle.load_settings()

        self.assertTrue(WindowSettings().geometry.isEmpty())
        self.assertTrue(WindowSettings().layout_state.isEmpty())
        start_tray.assert_called_once_with()


class ProxyFallbackTests(TemporarySettingsTest):

    def test_out_of_range_port_does_not_replace_the_current_proxy(self):
        SettingsManager.set("proxy/proxyEnable", True)
        SettingsManager.set("proxy/proxyType", "HttpProxy")
        SettingsManager.set("proxy/hostName", "proxy.example.com")
        SettingsManager.set("proxy/port", "65536")

        with (
            patch(
                "zapzap.core.environment.proxy_manager."
                "QtNetwork.QNetworkProxy.setApplicationProxy"
            ) as apply_proxy,
            self.assertLogs(
                "zapzap.core.environment.proxy_manager",
                level="WARNING",
            ),
        ):
            result = ProxyManager.apply()

        self.assertFalse(result.success)
        apply_proxy.assert_not_called()

    def test_qt_apply_error_is_returned_without_escaping(self):
        with (
            patch(
                "zapzap.core.environment.proxy_manager."
                "QtNetwork.QNetworkProxy.setApplicationProxy",
                side_effect=RuntimeError("simulated Qt failure"),
            ),
            self.assertLogs(
                "zapzap.core.environment.proxy_manager",
                level="ERROR",
            ),
        ):
            result = ProxyManager.apply()

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)


class ZoomFallbackTests(unittest.TestCase):

    def test_invalid_persisted_zoom_is_repaired(self):
        user = User(zoomFactor=float("nan"))
        user._persist = Mock()

        with self.assertLogs(
            "zapzap.features.accounts.domain.user",
            level="WARNING",
        ):
            self.assertEqual(user.zoomFactor, DEFAULT_ZOOM_FACTOR)

        user._persist.assert_called_once_with()

    def test_zoom_boundaries_match_qt_contract(self):
        self.assertEqual(User(zoomFactor=MIN_ZOOM_FACTOR).zoomFactor, 0.25)
        self.assertEqual(User(zoomFactor=MAX_ZOOM_FACTOR).zoomFactor, 5.0)

    def test_qt_failure_retries_with_default_zoom(self):
        view = Mock()
        view.setZoomFactor.side_effect = [RuntimeError("failure"), None]

        with self.assertLogs(
            "zapzap.features.accounts.domain.user",
            level="ERROR",
        ):
            applied = apply_zoom_factor(view, 2.0)

        self.assertEqual(applied, DEFAULT_ZOOM_FACTOR)
        self.assertEqual(
            [call.args[0] for call in view.setZoomFactor.call_args_list],
            [2.0, 1.0],
        )


class FakeDownload:
    def __init__(self, directory_failures=0):
        self.directory_failures = directory_failures
        self.directories = []
        self.cancel = Mock()

    def setDownloadDirectory(self, path):
        self.directories.append(path)
        if self.directory_failures:
            self.directory_failures -= 1
            raise RuntimeError("simulated directory failure")

    def downloadFileName(self):
        return "file.txt"

    def suggestedFileName(self):
        return "file.txt"

    def mimeType(self):
        return "text/plain"

    def url(self):
        return SimpleNamespace(toString=lambda: "https://example.com/file.txt")

    def setDownloadFileName(self, _name):
        raise AssertionError("the normalized name should already match")


class DownloadFallbackTests(TemporarySettingsTest):

    def test_invalid_download_path_is_repaired(self):
        SettingsManager.set("system/download_path", 42)
        with self.assertLogs(
            "zapzap.features.downloads.download_manager",
            level="WARNING",
        ):
            path = DownloadManager.get_path()
        self.assertEqual(path, DownloadManager.DOWNLOAD_PATH)

    def test_download_retries_with_default_directory(self):
        SettingsManager.set("system/download_path", "/configured")
        download = FakeDownload(directory_failures=1)

        with self.assertLogs(
            "zapzap.features.downloads.download_manager",
            level="ERROR",
        ):
            self.assertTrue(
                DownloadManager._set_initial_download_parameters(download)
            )

        self.assertEqual(
            download.directories,
            ["/configured", DownloadManager.DOWNLOAD_PATH],
        )
        download.cancel.assert_not_called()

    def test_download_is_cancelled_when_both_targets_fail(self):
        download = FakeDownload(directory_failures=2)

        with self.assertLogs(
            "zapzap.features.downloads.download_manager",
            level="ERROR",
        ):
            self.assertFalse(
                DownloadManager._set_initial_download_parameters(download)
            )

        download.cancel.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
