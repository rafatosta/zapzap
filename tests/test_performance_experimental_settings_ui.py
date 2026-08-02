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

    def test_send_with_ctrl_enter_sits_with_the_other_web_behavior_rows(self):
        page = PerformanceExperimentalSettingsController()

        self.assertEqual(
            page.send_with_ctrl_enter_row.title_label.text(),
            "Send messages with Ctrl+Enter",
        )
        self.assertIn(
            "new line",
            page.send_with_ctrl_enter_row.description_label.text(),
        )
        self.assertTrue(page.send_with_ctrl_enter.toolTip())
        self.assertFalse(page.send_with_ctrl_enter.isChecked())

        page.send_with_ctrl_enter.click()

        self.assertTrue(
            page.model.get_boolean_setting("send_with_ctrl_enter")
        )
        # The script is inserted while the profile is built, so rebuilding the
        # interface is enough; the whole process does not have to restart.
        self.assertEqual(
            page.restart_bar.restart_kind,
            SettingsRestartBar.INTERFACE,
        )
