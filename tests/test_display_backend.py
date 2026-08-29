"""Tests for Qt display backend selection and legacy migration."""

from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from PyQt6.QtCore import QSettings

from zapzap.core.config.settings.system import DisplayBackend, SystemSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager


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


class DisplayBackendSettingsTests(TemporarySettingsTest):

    def test_default_is_automatic_and_uses_the_new_key(self):
        settings = SystemSettings()

        self.assertEqual(settings.display_backend, DisplayBackend.AUTO)
        self.assertEqual(
            SettingsManager.get("system/display_backend"),
            DisplayBackend.AUTO.value,
        )

    def test_legacy_true_migrates_to_forced_wayland(self):
        SettingsManager.set("system/wayland", True)

        self.assertEqual(
            SystemSettings().display_backend,
            DisplayBackend.WAYLAND,
        )
        self.assertEqual(
            SettingsManager.get("system/display_backend"),
            DisplayBackend.WAYLAND.value,
        )
        self.assertTrue(SettingsManager.get("system/wayland", False))

    def test_legacy_false_migrates_to_automatic_instead_of_xcb(self):
        SettingsManager.set("system/wayland", False)

        self.assertEqual(SystemSettings().display_backend, DisplayBackend.AUTO)
        self.assertEqual(
            SettingsManager.get("system/display_backend"),
            DisplayBackend.AUTO.value,
        )
        self.assertFalse(SettingsManager.get("system/wayland", True))

    def test_invalid_backend_is_repaired_to_automatic(self):
        SettingsManager.set("system/display_backend", "invalid")

        self.assertEqual(SystemSettings().display_backend, DisplayBackend.AUTO)
        self.assertEqual(
            SettingsManager.get("system/display_backend"),
            DisplayBackend.AUTO.value,
        )

    def test_new_backend_choice_keeps_the_legacy_boolean_synchronized(self):
        settings = SystemSettings()

        settings.display_backend = DisplayBackend.WAYLAND
        self.assertTrue(SettingsManager.get("system/wayland", False))

        settings.display_backend = DisplayBackend.XCB
        self.assertFalse(SettingsManager.get("system/wayland", True))


class DisplayBackendSelectionTests(TemporarySettingsTest):

    def _platform(self, session_type, backend=DisplayBackend.AUTO):
        SystemSettings().display_backend = backend
        environment = {"XDG_SESSION_TYPE": session_type}
        with (
            patch.dict(
                "zapzap.core.environment.setup_manager.environ",
                environment,
                clear=True,
            ),
            patch.object(sys, "argv", ["zapzap"]),
            patch("zapzap.core.environment.setup_manager.IS_WINDOWS", False),
            patch("zapzap.core.environment.setup_manager.IS_MAC", False),
        ):
            return SetupManager.get_qt_platform()

    def test_automatic_uses_wayland_for_a_wayland_session(self):
        self.assertEqual(self._platform("wayland"), "wayland")

    def test_automatic_uses_xcb_for_an_x11_session(self):
        self.assertEqual(self._platform("x11"), "xcb")

    def test_explicit_wayland_ignores_the_session_type(self):
        self.assertEqual(
            self._platform("x11", DisplayBackend.WAYLAND),
            "wayland",
        )

    def test_explicit_xcb_is_honored_in_a_wayland_session(self):
        self.assertEqual(
            self._platform("wayland", DisplayBackend.XCB),
            "xcb",
        )

    def test_external_qt_platform_override_is_preserved(self):
        environment = {
            "QT_QPA_PLATFORM": "minimal",
            "XDG_SESSION_TYPE": "wayland",
        }
        with (
            patch.dict(
                "zapzap.core.environment.setup_manager.environ",
                environment,
                clear=True,
            ),
            patch.object(sys, "argv", ["zapzap"]),
            patch("zapzap.core.environment.setup_manager.IS_WINDOWS", False),
            patch("zapzap.core.environment.setup_manager.IS_MAC", False),
        ):
            self.assertIsNone(SetupManager.get_qt_platform())
            self.assertEqual(os.environ["QT_QPA_PLATFORM"], "minimal")

    def test_wayland_cli_argument_precedes_the_saved_setting(self):
        SystemSettings().display_backend = DisplayBackend.XCB
        environment = {"XDG_SESSION_TYPE": "x11"}
        with (
            patch.dict(
                "zapzap.core.environment.setup_manager.environ",
                environment,
                clear=True,
            ),
            patch.object(sys, "argv", ["zapzap", "--wayland"]),
            patch("zapzap.core.environment.setup_manager.IS_WINDOWS", False),
            patch("zapzap.core.environment.setup_manager.IS_MAC", False),
        ):
            self.assertEqual(SetupManager.get_qt_platform(), "wayland")

    def test_windows_and_macos_leave_platform_selection_to_qt(self):
        for platform_name in ("IS_WINDOWS", "IS_MAC"):
            with self.subTest(platform_name=platform_name):
                patches = {
                    "IS_WINDOWS": platform_name == "IS_WINDOWS",
                    "IS_MAC": platform_name == "IS_MAC",
                }
                with (
                    patch.dict(
                        "zapzap.core.environment.setup_manager.environ",
                        {},
                        clear=True,
                    ),
                    patch.object(sys, "argv", ["zapzap"]),
                    patch(
                        "zapzap.core.environment.setup_manager.IS_WINDOWS",
                        patches["IS_WINDOWS"],
                    ),
                    patch(
                        "zapzap.core.environment.setup_manager.IS_MAC",
                        patches["IS_MAC"],
                    ),
                ):
                    self.assertIsNone(SetupManager.get_qt_platform())


if __name__ == "__main__":
    unittest.main()
