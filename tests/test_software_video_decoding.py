"""Tests for the optional QtWebEngine software video decoding workaround."""

import ast
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import PropertyMock, patch

from PyQt6.QtCore import QSettings

from zapzap.core.config.dictionary_store import (
    DictionaryStore,
    DictionaryStorePreparation,
)
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import (
    SetupManager,
    STRICT_PROXY_WEBRTC_FLAG,
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

    def test_corrupt_environment_flag_value_is_treated_as_empty(self):
        environment = {"QTWEBENGINE_CHROMIUM_FLAGS": 42}

        update_chromium_flag(VIDEO_DECODE_FLAG, True, environment)

        self.assertEqual(
            environment["QTWEBENGINE_CHROMIUM_FLAGS"],
            VIDEO_DECODE_FLAG,
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

    def _strict_proxy_flags(
        self,
        *,
        proxy_enabled,
        proxy_type,
        strict_enabled,
        existing="--existing",
    ):
        values = {
            "proxy/proxyEnable": proxy_enabled,
            "proxy/proxyType": proxy_type,
            "proxy/hostName": "proxy.example.com",
            "proxy/port": "8080",
            "privacy/strict_proxy": strict_enabled,
        }
        with (
            patch.dict(
                os.environ,
                {"QTWEBENGINE_CHROMIUM_FLAGS": existing},
                clear=True,
            ),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation("/tmp/dictionaries"),
            ),
            patch(
                "zapzap.core.environment.setup_manager.preferred_render_node",
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
                side_effect=lambda key, default=None: values.get(key, default),
            ),
            patch.object(
                PerformanceSettings,
                "js_memory_limit_mb",
                new_callable=PropertyMock,
                return_value=0,
            ),
            patch.object(
                PerformanceSettings,
                "get_boolean_setting",
                return_value=False,
            ),
        ):
            SetupManager.apply()
            return os.environ["QTWEBENGINE_CHROMIUM_FLAGS"].split()

    def test_strict_proxy_flag_only_applies_to_explicit_proxy_types(self):
        cases = (
            (True, "HttpProxy", True, True),
            (True, "Socks5Proxy", True, True),
            (True, "NoProxy", True, False),
            (True, "DefaultProxy", True, False),
            (True, "HttpCachingProxy", True, False),
            (True, "FtpCachingProxy", True, False),
            (False, "HttpProxy", True, False),
            (True, "HttpProxy", False, False),
        )
        for proxy_enabled, proxy_type, strict_enabled, expected in cases:
            with self.subTest(
                proxy_enabled=proxy_enabled,
                proxy_type=proxy_type,
                strict_enabled=strict_enabled,
            ):
                flags = self._strict_proxy_flags(
                    proxy_enabled=proxy_enabled,
                    proxy_type=proxy_type,
                    strict_enabled=strict_enabled,
                )
                self.assertEqual(
                    flags.count(STRICT_PROXY_WEBRTC_FLAG),
                    1 if expected else 0,
                )
                self.assertIn("--existing", flags)

    def test_strict_proxy_flag_is_deduplicated_and_removed_when_inactive(self):
        duplicate = (
            f"--first {STRICT_PROXY_WEBRTC_FLAG} "
            f"{STRICT_PROXY_WEBRTC_FLAG} --last"
        )
        active_flags = self._strict_proxy_flags(
            proxy_enabled=True,
            proxy_type="HttpProxy",
            strict_enabled=True,
            existing=duplicate,
        )
        inactive_flags = self._strict_proxy_flags(
            proxy_enabled=True,
            proxy_type="DefaultProxy",
            strict_enabled=True,
            existing=duplicate,
        )

        self.assertEqual(active_flags.count(STRICT_PROXY_WEBRTC_FLAG), 1)
        self.assertNotIn(STRICT_PROXY_WEBRTC_FLAG, inactive_flags)
        self.assertEqual(inactive_flags[:2], ["--first", "--last"])

    def test_strict_proxy_flag_requires_a_valid_explicit_endpoint(self):
        values = {
            "proxy/proxyEnable": True,
            "proxy/proxyType": "HttpProxy",
            "proxy/hostName": "",
            "proxy/port": "8080",
            "privacy/strict_proxy": True,
        }
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation("/tmp/dictionaries"),
            ),
            patch(
                "zapzap.core.environment.setup_manager.preferred_render_node",
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
                side_effect=lambda key, default=None: values.get(key, default),
            ),
            patch.object(
                PerformanceSettings,
                "js_memory_limit_mb",
                new_callable=PropertyMock,
                return_value=0,
            ),
            patch.object(
                PerformanceSettings,
                "get_boolean_setting",
                return_value=False,
            ),
        ):
            SetupManager.apply()
            flags = os.environ["QTWEBENGINE_CHROMIUM_FLAGS"].split()

        self.assertNotIn(STRICT_PROXY_WEBRTC_FLAG, flags)

    def test_setup_manager_applies_the_persisted_setting(self):
        environment = {"QTWEBENGINE_CHROMIUM_FLAGS": "--existing"}
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(
                PerformanceSettings,
                "get_boolean_setting",
                return_value=True,
            ),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation("/tmp/dictionaries"),
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
        webview_factory_call = next(
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "load_webview_factory"
        )

        self.assertLess(setup_call.lineno, webview_factory_call.lineno)
        self.assertLess(setup_call.lineno, application_call.lineno)

    def test_global_proxy_is_applied_before_main_window_creation(self):
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

        proxy_call = next(
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "ProxyManager"
            and node.func.attr == "apply"
        )
        application_call = next(
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "SingleApplication"
        )
        interface_call = next(
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "startInterface"
        )

        self.assertLess(application_call.lineno, proxy_call.lineno)
        self.assertLess(proxy_call.lineno, interface_call.lineno)

    def test_js_memory_index_value_reaches_the_chromium_flag(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(
                DictionaryStore,
                "prepare",
                return_value=DictionaryStorePreparation("/tmp/dictionaries"),
            ),
            patch(
                "zapzap.core.environment.setup_manager.preferred_render_node",
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
            patch.object(
                PerformanceSettings,
                "js_memory_limit_mb",
                new_callable=PropertyMock,
                return_value=1024,
            ),
        ):
            SetupManager.apply()
            flags = os.environ["QTWEBENGINE_CHROMIUM_FLAGS"].split()

        self.assertIn(
            "--js-flags=--max-old-space-size=1024",
            flags,
        )


if __name__ == "__main__":
    unittest.main()
