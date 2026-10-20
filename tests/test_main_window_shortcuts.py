"""Regression tests for main-window keyboard shortcuts."""

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy, QTest
from PyQt6.QtWidgets import QApplication

from qt_test_case import QtTestCase
from zapzap.ui.components.main_window import MainWindowView


class MainWindowShortcutTests(QtTestCase):

    def test_ctrl_j_opens_the_downloads_action_from_view_menu(self):
        window = MainWindowView()
        self.addCleanup(window.deleteLater)

        self.assertEqual(window.actionDownloads.shortcut().toString(), "Ctrl+J")
        self.assertEqual(window.actionDownloads.text(), "Downloads")
        self.assertIn(window.actionDownloads, window.menuView.actions())

    def test_keyboard_shortcuts_action_registers_one_single_step_shortcut(self):
        window = MainWindowView()
        self.addCleanup(window.deleteLater)

        shortcuts = window.actionShortcuts.shortcuts()

        self.assertEqual([shortcut.toString() for shortcut in shortcuts], ["Ctrl+?"])
        self.assertEqual(shortcuts[0].count(), 1)
        self.assertIn(window.actionShortcuts, window.menuHelp.actions())

    def test_ctrl_question_mark_triggers_the_keyboard_shortcuts_action(self):
        window = MainWindowView()
        self.addCleanup(window.deleteLater)
        window.show()
        window.activateWindow()
        QApplication.processEvents()
        triggered = QSignalSpy(window.actionShortcuts.triggered)

        QTest.keyClick(
            window,
            Qt.Key.Key_Question,
            Qt.KeyboardModifier.ControlModifier,
        )
        QApplication.processEvents()

        self.assertEqual(len(triggered), 1)


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
