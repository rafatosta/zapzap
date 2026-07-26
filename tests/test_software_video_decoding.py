"""Tests for the optional QtWebEngine software video decoding workaround."""

import ast
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PyQt6.QtCore import QSettings

from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import (
    SetupManager,
    update_chromium_flag,
)


VIDEO_DECODE_FLAG = "--disable-accelerated-video-decode"


class ChromiumFlagTests(unittest.TestCase):

    def test_adds_flag_and_preserves_existing_flags(self):
        environment = {
            "QTWEBENGINE_CHROMIUM_FLAGS": "--enable-features=UseOzonePlatform"
        }

        update_chromium_flag(VIDEO_DECODE_FLAG, True, environment)

        self.assertEqual(
            environment["QTWEBENGINE_CHROMIUM_FLAGS"],
            "--enable-features=UseOzonePlatform "
            "--disable-accelerated-video-decode",
        )

    def test_does_not_duplicate_existing_flag_or_change_its_order(self):
        environment = {
            "QTWEBENGINE_CHROMIUM_FLAGS": (
                f"{VIDEO_DECODE_FLAG} --enable-features=UseOzonePlatform "
                f"{VIDEO_DECODE_FLAG}"
            )
        }

        update_chromium_flag(VIDEO_DECODE_FLAG, True, environment)

        self.assertEqual(
            environment["QTWEBENGINE_CHROMIUM_FLAGS"],
            f"{VIDEO_DECODE_FLAG} --enable-features=UseOzonePlatform",
        )

    def test_removes_only_the_exact_flag(self):
        environment = {
            "QTWEBENGINE_CHROMIUM_FLAGS": (
                f"{VIDEO_DECODE_FLAG} "
                "--disable-accelerated-video-decode-extra "
                "--enable-features=UseOzonePlatform"
            )
        }

        update_chromium_flag(VIDEO_DECODE_FLAG, False, environment)

        self.assertEqual(
            environment["QTWEBENGINE_CHROMIUM_FLAGS"],
            "--disable-accelerated-video-decode-extra "
            "--enable-features=UseOzonePlatform",
        )

    def test_handles_empty_values_and_extra_spaces(self):
        empty_environment = {}
        spaced_environment = {
            "QTWEBENGINE_CHROMIUM_FLAGS": "   --foo   --bar   "
        }

        update_chromium_flag(VIDEO_DECODE_FLAG, False, empty_environment)
        update_chromium_flag(VIDEO_DECODE_FLAG, True, spaced_environment)

        self.assertEqual(empty_environment["QTWEBENGINE_CHROMIUM_FLAGS"], "")
        self.assertEqual(
            spaced_environment["QTWEBENGINE_CHROMIUM_FLAGS"],
            f"--foo --bar {VIDEO_DECODE_FLAG}",
        )


class SoftwareVideoDecodingPersistenceTests(unittest.TestCase):

    def setUp(self):
        self._previous_settings = SettingsManager._settings
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.settings_path = (
            Path(self._temporary_directory.name) / "performance.ini"
        )
        SettingsManager._settings = QSettings(
            str(self.settings_path),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        self._temporary_directory.cleanup()

    def _reload_settings(self):
        SettingsManager._settings.sync()
        SettingsManager._settings = QSettings(
            str(self.settings_path),
            QSettings.Format.IniFormat,
        )
        return PerformanceSettings()

    def test_setting_is_disabled_by_default(self):
        self.assertFalse(
            PerformanceSettings().get_boolean_setting(
                "software_video_decoding"
            )
        )

    def test_activation_and_deactivation_persist_after_reload(self):
        settings = PerformanceSettings()
        settings.set_boolean_setting("software_video_decoding", True)
        self.assertTrue(
            self._reload_settings().get_boolean_setting(
                "software_video_decoding"
            )
        )

        PerformanceSettings().set_boolean_setting(
            "software_video_decoding",
            False,
        )
        self.assertFalse(
            self._reload_settings().get_boolean_setting(
                "software_video_decoding"
            )
        )


class SoftwareVideoDecodingStartupTests(unittest.TestCase):

    def test_setup_manager_applies_the_persisted_setting(self):
        environment = {"QTWEBENGINE_CHROMIUM_FLAGS": "--existing"}
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(
                PerformanceSettings,
                "get_boolean_setting",
                return_value=True,
            ),
            patch(
                "zapzap.core.environment.setup_manager."
                "DictionariesManager.get_path",
                return_value="/tmp/dictionaries",
            ),
            patch(
                "zapzap.core.environment.setup_manager."
                "preferred_render_node",
                return_value=None,
            ),
            patch(
                "zapzap.core.environment.setup_manager."
                "has_headless_secondary_gpu",
                return_value=False,
            ),
            patch.object(
                SettingsManager,
                "get",
                side_effect=lambda _key, default=None: default,
            ),
        ):
            SetupManager.apply()
            flags = os.environ["QTWEBENGINE_CHROMIUM_FLAGS"].split()

        self.assertIn("--existing", flags)
        self.assertIn(VIDEO_DECODE_FLAG, flags)

    def test_environment_setup_precedes_application_creation(self):
        application_path = (
            Path(__file__).resolve().parents[1]
            / "zapzap"
            / "app"
            / "application.py"
        )
        tree = ast.parse(application_path.read_text(encoding="utf-8"))
        main = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )

        setup_call = next(
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "SetupManager"
            and node.func.attr == "apply"
        )
        application_call = next(
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "SingleApplication"
        )

        self.assertLess(setup_call.lineno, application_call.lineno)


if __name__ == "__main__":
    unittest.main()
