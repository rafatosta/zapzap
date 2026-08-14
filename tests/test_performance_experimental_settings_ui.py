"""UI regression tests for experimental performance settings."""

from qt_test_case import QtTestCase
from zapzap.core.config.settings.performance import MAX_HTTP_CACHE_MIB
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.ui.components import SettingsRestartBar
from zapzap.features.settings.pages.performance_experimental.controller import (
    PerformanceExperimentalSettingsController,
)


class PerformanceExperimentalSettingsUiTests(QtTestCase):

    def setUp(self):
        SettingsManager.clear()

    def test_software_video_decoding_uses_gpu_section_and_full_restart(self):
        page = PerformanceExperimentalSettingsController()

        self.assertEqual(
            page.software_video_decoding_row.title_label.text(),
            "Use software video decoding",
        )
        self.assertIn(
            "CPU and battery usage",
            page.software_video_decoding_row.description_label.text(),
        )
        self.assertFalse(page.software_video_decoding.isChecked())

        page.software_video_decoding.click()

        self.assertTrue(
            page.model.get_boolean_setting("software_video_decoding")
        )
        self.assertEqual(
            page.restart_bar.restart_kind,
            SettingsRestartBar.APPLICATION,
        )

    def test_http_cache_selector_uses_qt_safe_mib_values(self):
        page = PerformanceExperimentalSettingsController()
        values = [
            page.cache_size_max.itemData(index)
            for index in range(page.cache_size_max.count())
        ]

        self.assertEqual(values[0], 0)
        self.assertEqual(values[-1], MAX_HTTP_CACHE_MIB)
        self.assertTrue(all(value <= MAX_HTTP_CACHE_MIB for value in values))
        self.assertNotIn(2048, values)
        self.assertEqual(
            page.cache_size_max.itemText(page.cache_size_max.count() - 1),
            "2047 MiB",
        )
        self.assertIn(
            "automatic",
            page.cache_size_max_row.description_label.text(),
        )
        self.assertIn("2047 MiB", page.cache_size_max.toolTip())
