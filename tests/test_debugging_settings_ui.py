"""Regression tests for the compact Debugging settings page."""

import json
import unittest

from PyQt6.QtWidgets import QApplication

from qt_test_case import QtTestCase
from zapzap.features.settings.pages.debugging.controller import (
    DebuggingSettingsController,
)
from zapzap.features.settings.pages.debugging.view import DebuggingSettingsView
from zapzap.core.diagnostics.runtime_environment_debug import (
    RuntimeEnvironmentDebug,
)
from zapzap.ui.primitives import Button


class DebuggingSettingsUiTests(QtTestCase):

    def test_destructive_reset_is_isolated_in_maintenance(self):
        page = DebuggingSettingsView()

        self.assertEqual(page.btn_reset_settings.text(), "Reset…")
        self.assertEqual(page.btn_reset_settings.variant, Button.DANGER)
        self.assertIn("restarted", page.reset_settings_row.description_label.text())
        self.assertFalse(hasattr(page, "btn_delete_old_debug_logs"))

    def test_cleanup_actions_share_one_contextual_menu(self):
        page = DebuggingSettingsView()

        self.assertIs(page.btn_cleanup_debug_logs.menu(), page.cleanup_menu)
        self.assertEqual(
            page.action_delete_old_debug_logs.text(),
            "Delete old files",
        )
        self.assertEqual(
            page.action_delete_all_debug_logs.text(),
            "Delete all logs and reports",
        )
        self.assertTrue(page.action_delete_all_debug_logs.toolTip())

    def test_file_summary_uses_correct_plural_and_log_count(self):
        page = DebuggingSettingsView()

        page.set_debug_logs_details("/tmp/zapzap-debug", 1, True)
        self.assertEqual(
            page.label_debug_logs_hint.text(),
            "1 crash report and 1 log file",
        )
        page.set_debug_logs_details("/tmp/zapzap-debug", 3, False)
        self.assertEqual(page.label_debug_logs_hint.text(), "3 crash reports")

    def test_runtime_summary_and_raw_details_update_together(self):
        page = DebuggingSettingsView()
        payload = json.dumps(
            {
                "app": {
                    "version": "7.0.3",
                    "packaging": "Flatpak",
                    "build_channel": "stable",
                },
                "qt": {"qt_version": "6.11.1", "pyqt_version": "6.11.0"},
                "python": {"python_version": "3.14.0 (main)"},
                "distro": {
                    "host_distro": {"PRETTY_NAME": "Example Linux"},
                },
                "app_config": {
                    "graphics_session": {
                        "xdg_session_type": "wayland",
                        "qt_platform_name": "xcb",
                    },
                },
            }
        )

        page.set_runtime_environment(payload)
        labels = [
            page.runtime_summary_layout.itemAt(index).widget().key_label.text()
            for index in range(page.runtime_summary_layout.count())
        ]
        values = [
            page.runtime_summary_layout.itemAt(index).widget().value_label.text()
            for index in range(page.runtime_summary_layout.count())
        ]
        self.assertEqual(
            values,
            [
                "7.0.3",
                "Flatpak",
                "stable",
                "6.11.1",
                "6.11.0",
                "3.14.0",
                "Example Linux",
                "Wayland",
                "X11/XWayland",
            ],
        )
        self.assertEqual(
            labels[-2:],
            ["System graphics session", "ZapZap graphics backend"],
        )
        self.assertEqual(page.runtime_environment.toPlainText(), payload)
        self.assertFalse(page.runtime_details.toggle.isChecked())
        self.assertFalse(page.runtime_details.content.isVisible())

    def test_runtime_report_records_the_effective_qt_graphics_backend(self):
        graphics = (
            RuntimeEnvironmentDebug()
            .build_report()["app_config"]["graphics_session"]
        )

        self.assertEqual(
            graphics["qt_platform_name"],
            QApplication.platformName(),
        )

    def test_copy_actions_copy_complete_data_and_show_feedback(self):
        page = DebuggingSettingsController()

        page.btn_copy_runtime.click()
        self.assertEqual(QApplication.clipboard().text(), page.runtime_json())
        self.assertEqual(page.btn_copy_runtime.text(), "Details copied")

        page.btn_copy_debug_logs_path.click()
        self.assertEqual(
            QApplication.clipboard().text(),
            page.debug_logs_path.full_path,
        )
        self.assertEqual(page.btn_copy_debug_logs_path.text(), "Path copied")


if __name__ == "__main__":
    unittest.main()
