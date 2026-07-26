"""Regression tests for restoring the maximized state of hidden windows."""

import unittest

from PyQt6.QtWidgets import QWidget

from qt_test_case import QtTestCase
from zapzap.ui.main_window.window_state import WindowStateMemory


class _Window(WindowStateMemory, QWidget):
    """Stand-in wired like the application windows."""

    def __init__(self):
        super().__init__()
        self.is_fullscreen = False

    def hideEvent(self, event):
        self.remember_window_state()
        super().hideEvent(event)

    def restore_window(self):
        self.show_in_remembered_state(self.is_fullscreen)


class _DelegatingWrapper(WindowStateMemory, QWidget):
    """Wrapper that forwards unknown attributes, like the CSR window."""

    def __init__(self, inner):
        super().__init__()
        self.inner_window = inner

    def __getattr__(self, name):
        return getattr(self.inner_window, name)


class WindowStateRestoreTest(QtTestCase):
    def setUp(self):
        self.window = _Window()
        self.addCleanup(self.window.deleteLater)

    def test_maximized_window_is_restored_maximized(self):
        self.window.showMaximized()
        self.assertTrue(self.window.isMaximized())

        self.window.hide()
        self.window.restore_window()

        self.assertTrue(self.window.isMaximized())

    def test_normal_window_is_restored_normal(self):
        self.window.showNormal()

        self.window.hide()
        self.window.restore_window()

        self.assertFalse(self.window.isMaximized())

    def test_fullscreen_takes_precedence_over_maximized(self):
        self.window.showMaximized()
        self.window.hide()
        self.window.is_fullscreen = True

        self.window.restore_window()

        self.assertTrue(self.window.isFullScreen())

    def test_window_never_hidden_is_shown_normal(self):
        self.window.show_in_remembered_state()

        self.assertFalse(self.window.isMaximized())

    def test_restoring_twice_keeps_the_state(self):
        self.window.showMaximized()

        for _ in range(2):
            self.window.hide()
            self.window.restore_window()

        self.assertTrue(self.window.isMaximized())

    def test_state_is_not_read_from_a_delegated_inner_window(self):
        inner = _Window()
        self.addCleanup(inner.deleteLater)
        inner.showMaximized()
        inner.hide()
        wrapper = _DelegatingWrapper(inner)
        self.addCleanup(wrapper.deleteLater)

        wrapper.show_in_remembered_state()

        self.assertFalse(wrapper.isMaximized())


if __name__ == "__main__":
    unittest.main()
