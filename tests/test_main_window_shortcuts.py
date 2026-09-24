"""Regression tests for main-window keyboard shortcuts."""

from qt_test_case import QtTestCase
from zapzap.ui.components.main_window import MainWindowView


class MainWindowShortcutTests(QtTestCase):

    def test_ctrl_j_opens_the_downloads_action_from_view_menu(self):
        window = MainWindowView()
        self.addCleanup(window.deleteLater)

        self.assertEqual(window.actionDownloads.shortcut().toString(), "Ctrl+J")
        self.assertEqual(window.actionDownloads.text(), "Downloads")
        self.assertIn(window.actionDownloads, window.menuView.actions())


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
