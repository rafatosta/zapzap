"""Regression tests for the Qt WebEngine HTTP cache size boundary."""

from pathlib import Path
import tempfile
import unittest

from PyQt6.QtCore import QSettings

from zapzap.core.config.settings.performance import AUTO_HTTP_CACHE_SIZE
from zapzap.core.config.settings.performance import DEFAULT_HTTP_CACHE_TYPE
from zapzap.core.config.settings.performance import INT32_MAX
from zapzap.core.config.settings.performance import MAX_HTTP_CACHE_MIB
from zapzap.core.config.settings.performance import MEBIBYTE
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings.performance import apply_http_cache_size
from zapzap.core.config.settings.performance import apply_http_cache_type
from zapzap.core.config.settings.performance import apply_persistent_cookies_policy
from zapzap.core.config.settings.performance import http_cache_size_bytes
from zapzap.core.config.settings.performance import normalize_http_cache_mib
from zapzap.core.config.settings.performance import normalize_http_cache_type
from zapzap.core.config.settings_manager import SettingsManager


class FakeProfile:

    def __init__(self, failures=0):
        self.failures = failures
        self.cache_sizes = []
        self.cache_types = []
        self.cookie_policies = []

    def setHttpCacheMaximumSize(self, cache_bytes):
        self.cache_sizes.append(cache_bytes)
        if self.failures:
            self.failures -= 1
            raise OverflowError("simulated Qt failure")

    def setHttpCacheType(self, cache_type):
        self.cache_types.append(cache_type)
        if self.failures:
            self.failures -= 1
            raise RuntimeError("simulated Qt failure")

    def setPersistentCookiesPolicy(self, policy):
        self.cookie_policies.append(policy)
        if self.failures:
            self.failures -= 1
            raise RuntimeError("simulated Qt failure")


class HttpCacheNormalizationTests(unittest.TestCase):

    def test_accepts_qt_safe_values(self):
        self.assertEqual(normalize_http_cache_mib(0), 0)
        self.assertEqual(normalize_http_cache_mib(1), 1)
        self.assertEqual(normalize_http_cache_mib(2047), 2047)
        self.assertEqual(normalize_http_cache_mib("128"), 128)
        self.assertEqual(http_cache_size_bytes(1), MEBIBYTE)
        self.assertLessEqual(
            http_cache_size_bytes(MAX_HTTP_CACHE_MIB),
            INT32_MAX,
        )

    def test_invalid_values_use_automatic_management(self):
        for value in (2048, 10**100, -1, "", "invalid", None):
            with self.subTest(value=value):
                self.assertEqual(
                    normalize_http_cache_mib(value),
                    AUTO_HTTP_CACHE_SIZE,
                )
                self.assertEqual(
                    http_cache_size_bytes(value),
                    AUTO_HTTP_CACHE_SIZE,
                )


class HttpCacheApplicationTests(unittest.TestCase):

    def test_applies_the_normalized_byte_count(self):
        profile = FakeProfile()

        applied_mib = apply_http_cache_size(profile, "2047")

        self.assertEqual(applied_mib, MAX_HTTP_CACHE_MIB)
        self.assertEqual(
            profile.cache_sizes,
            [MAX_HTTP_CACHE_MIB * MEBIBYTE],
        )

    def test_invalid_value_never_reaches_qt_as_an_oversized_byte_count(self):
        profile = FakeProfile()

        applied_mib = apply_http_cache_size(profile, 2048)

        self.assertEqual(applied_mib, AUTO_HTTP_CACHE_SIZE)
        self.assertEqual(profile.cache_sizes, [AUTO_HTTP_CACHE_SIZE])

    def test_qt_failure_retries_with_automatic_management(self):
        profile = FakeProfile(failures=1)

        with self.assertLogs(
            "zapzap.core.config.settings.performance",
            level="ERROR",
        ):
            applied_mib = apply_http_cache_size(profile, 512)

        self.assertEqual(applied_mib, AUTO_HTTP_CACHE_SIZE)
        self.assertEqual(profile.cache_sizes, [512 * MEBIBYTE, 0])

    def test_failure_of_automatic_fallback_does_not_escape(self):
        profile = FakeProfile(failures=2)

        with self.assertLogs(
            "zapzap.core.config.settings.performance",
            level="ERROR",
        ) as captured:
            applied_mib = apply_http_cache_size(profile, 512)

        self.assertEqual(applied_mib, AUTO_HTTP_CACHE_SIZE)
        self.assertEqual(profile.cache_sizes, [512 * MEBIBYTE, 0])
        self.assertEqual(len(captured.records), 2)

    def test_invalid_cache_type_is_normalized_before_reaching_qt(self):
        profile = FakeProfile()
        cache_types = {
            "MemoryHttpCache": 1,
            "DiskHttpCache": 2,
            "NoCache": 3,
        }

        applied = apply_http_cache_type(profile, "unknown", cache_types)

        self.assertEqual(applied, DEFAULT_HTTP_CACHE_TYPE)
        self.assertEqual(profile.cache_types, [2])

    def test_cache_type_qt_failure_retries_with_disk_cache(self):
        profile = FakeProfile(failures=1)
        cache_types = {
            "MemoryHttpCache": 1,
            "DiskHttpCache": 2,
            "NoCache": 3,
        }

        with self.assertLogs(
            "zapzap.core.config.settings.performance",
            level="ERROR",
        ):
            applied = apply_http_cache_type(
                profile,
                "MemoryHttpCache",
                cache_types,
            )

        self.assertEqual(applied, DEFAULT_HTTP_CACHE_TYPE)
        self.assertEqual(profile.cache_types, [1, 2])

    def test_cookie_policy_qt_failure_retries_with_persistence(self):
        profile = FakeProfile(failures=1)

        with self.assertLogs(
            "zapzap.core.config.settings.performance",
            level="ERROR",
        ):
            applied = apply_persistent_cookies_policy(
                profile,
                False,
                {False: "session", True: "persistent"},
            )

        self.assertTrue(applied)
        self.assertEqual(profile.cookie_policies, ["session", "persistent"])


class HttpCachePersistenceTests(unittest.TestCase):

    def setUp(self):
        self._previous_settings = SettingsManager._settings
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.settings_path = Path(self._temporary_directory.name) / "cache.ini"
        SettingsManager._settings = QSettings(
            str(self.settings_path),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        self._temporary_directory.cleanup()

    def test_missing_key_uses_safe_default_without_creating_it(self):
        settings = PerformanceSettings()

        self.assertEqual(settings.cache_size_max, AUTO_HTTP_CACHE_SIZE)
        self.assertFalse(SettingsManager.contains("performance/cache_size_max"))

    def test_invalid_stored_value_is_logged_and_persisted_as_automatic(self):
        SettingsManager.set("performance/cache_size_max", "2048")

        with self.assertLogs(
            "zapzap.core.config.settings.performance",
            level="WARNING",
        ) as captured:
            cache_mib = PerformanceSettings().cache_size_max

        self.assertEqual(cache_mib, AUTO_HTTP_CACHE_SIZE)
        self.assertIn("accepted range: 0 to 2047 MiB", captured.output[0])
        self.assertEqual(
            int(SettingsManager.get("performance/cache_size_max")),
            AUTO_HTTP_CACHE_SIZE,
        )

    def test_all_corrupt_stored_values_are_repaired(self):
        for value in (-1, "", "invalid", None, 10**100):
            with self.subTest(value=value):
                SettingsManager.set("performance/cache_size_max", value)
                with self.assertLogs(
                    "zapzap.core.config.settings.performance",
                    level="WARNING",
                ):
                    self.assertEqual(
                        PerformanceSettings().cache_size_max,
                        AUTO_HTTP_CACHE_SIZE,
                    )
                self.assertEqual(
                    int(SettingsManager.get("performance/cache_size_max")),
                    AUTO_HTTP_CACHE_SIZE,
                )

    def test_invalid_cache_type_is_repaired(self):
        SettingsManager.set("performance/cache_type", "unknown")

        with self.assertLogs(
            "zapzap.core.config.settings.performance",
            level="WARNING",
        ):
            cache_type = PerformanceSettings().cache_type

        self.assertEqual(cache_type, DEFAULT_HTTP_CACHE_TYPE)
        self.assertEqual(
            SettingsManager.get("performance/cache_type"),
            DEFAULT_HTTP_CACHE_TYPE,
        )

    def test_js_memory_index_migrates_the_legacy_value(self):
        SettingsManager.set("performance/js_memory_limit_mb", "1024")

        settings = PerformanceSettings()

        self.assertEqual(settings.js_memory_limit_index, 2)
        self.assertEqual(settings.js_memory_limit_mb, 1024)
        self.assertEqual(
            int(SettingsManager.get("performance/js_memory_limit_index")),
            2,
        )

    def test_js_memory_index_keeps_the_legacy_key_in_sync(self):
        settings = PerformanceSettings()

        settings.js_memory_limit_index = 3

        self.assertEqual(settings.js_memory_limit_mb, 4096)
        self.assertEqual(
            int(SettingsManager.get("performance/js_memory_limit_mb")),
            4096,
        )


if __name__ == "__main__":
    unittest.main()
