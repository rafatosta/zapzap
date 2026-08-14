"""Regression tests for the Qt WebEngine HTTP cache size boundary."""

from pathlib import Path
import tempfile
import unittest

from PyQt6.QtCore import QSettings

from zapzap.core.config.settings.performance import AUTO_HTTP_CACHE_SIZE
from zapzap.core.config.settings.performance import INT32_MAX
from zapzap.core.config.settings.performance import MAX_HTTP_CACHE_MIB
from zapzap.core.config.settings.performance import MEBIBYTE
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings.performance import apply_http_cache_size
from zapzap.core.config.settings.performance import http_cache_size_bytes
from zapzap.core.config.settings.performance import normalize_http_cache_mib
from zapzap.core.config.settings_manager import SettingsManager


class FakeProfile:

    def __init__(self, failures=0):
        self.failures = failures
        self.cache_sizes = []

    def setHttpCacheMaximumSize(self, cache_bytes):
        self.cache_sizes.append(cache_bytes)
        if self.failures:
            self.failures -= 1
            raise OverflowError("simulated Qt failure")


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


if __name__ == "__main__":
    unittest.main()
