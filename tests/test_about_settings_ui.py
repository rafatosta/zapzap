"""Regression tests for the institutional About settings page."""

import unittest

from PyQt6.QtWidgets import QApplication, QPushButton

from qt_test_case import QtTestCase
from zapzap import __version__
from zapzap.features.settings.pages.about.controller import AboutSettingsController
from zapzap.features.settings.pages.about.model import AboutSettingsModel
from zapzap.features.settings.pages.about.view import AboutSettingsView


class AboutSettingsUiTests(QtTestCase):

    def test_identity_is_prominent_and_excludes_runtime_versions(self):
        page = AboutSettingsController()

        self.assertEqual(page.identity_header.name_label.text(), "ZapZap")
        self.assertIn(__version__, page.identity_header.version_label.text())
        self.assertNotIn("Qt", page.identity_header.version_label.text())
        self.assertEqual(page.identity_header.icon_label.width(), 72)

    def test_project_actions_are_full_clickable_rows_without_visible_urls(self):
        page = AboutSettingsController()

        for row in (page.homepage_row, page.issue_row, page.donate_row):
            self.assertIsInstance(row, QPushButton)
            self.assertTrue(row.accessibleName())
            self.assertNotIn("http", row.description_label.text())

    def test_technical_details_are_collapsed_and_hide_unknown_values(self):
        page = AboutSettingsController()

        self.assertFalse(page.technical_details.toggle.isChecked())
        self.assertFalse(page.technical_details.details_widget.isVisible())
        values = [value for _label, value in page.model.technical_details]
        self.assertNotIn("Unknown", values)

        page.technical_details.toggle.click()
        self.assertTrue(page.technical_details.toggle.isChecked())
        self.assertFalse(page.technical_details.details_widget.isHidden())

    def test_system_information_contains_runtime_versions(self):
        information = AboutSettingsModel().system_information

        self.assertIn(f"ZapZap {__version__}", information)
        self.assertIn("Qt:", information)
        self.assertIn("PyQt:", information)
        self.assertIn("Python:", information)
        self.assertNotIn("Unknown", information)

    def test_copy_action_updates_clipboard_and_shows_feedback(self):
        page = AboutSettingsController()

        page.copy_system_info_button.click()

        self.assertEqual(
            QApplication.clipboard().text(),
            page.model.system_information,
        )
        self.assertEqual(
            page.copy_system_info_button.text(),
            "Information copied",
        )

    def test_license_and_credits_actions_are_available(self):
        page = AboutSettingsView()

        self.assertEqual(page.license_row.description_label.text(), "GPL-3.0-or-later")
        self.assertTrue(page.license_row.accessibleName())
        self.assertTrue(page.credits_row.accessibleName())


if __name__ == "__main__":
    unittest.main()
