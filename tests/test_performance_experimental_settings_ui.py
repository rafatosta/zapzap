"""UI regression tests for experimental performance settings."""

from qt_test_case import QtTestCase
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
