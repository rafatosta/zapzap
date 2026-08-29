"""Regression tests for the shared native/CSR window lifecycle."""

from types import SimpleNamespace
from unittest.mock import patch

from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtWidgets import QMainWindow

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.app.window_lifecycle import ClientSideWindowHost, WindowLifecycle
from zapzap.core.config.settings.system import SystemSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.ui.components import ClientSideWindow


class _Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.background_preparations = 0
        self.lifecycle = WindowLifecycle(self, self)

    def hideEvent(self, event):
        self.lifecycle.remember_window_state(self)
        super().hideEvent(event)

    def closeEvent(self, event):
        self.lifecycle.close_event(event)

    def restore_window(self):
        self.lifecycle.restore_window()

    def show_window(self):
        self.lifecycle.show_window()

    def prepare_for_background(self):
        self.background_preparations += 1


class _Content(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = object()
        self.app_settings = None
        self.settings_opened = 0

    def attach_window_host(self, host, lifecycle):
        self.host = host
        self.lifecycle = lifecycle

    def prepare_for_background(self):
        pass

    def open_settings(self):
        self.settings_opened += 1

    def close_settings(self):
        pass

    def settings_menubar(self):
        pass

    def set_sidebar_visible(self, _visible, _animated=True, _persist=True):
        pass

    def xdgOpenChat(self, _url):
        pass


class _MainWindowContent(MainWindowController):
    def __init__(self, hide_results):
        self._hide_results = hide_results
        super().__init__(webview_factory=StubWebView, user_provider=lambda: [])

    def hideEvent(self, event):
        try:
            super().hideEvent(event)
        except RuntimeError as error:
            self._hide_results.append(error)
        else:
            self._hide_results.append(None)


class WindowStateRestoreTest(QtTestCase):
    def setUp(self):
        self.window = _Window()
        self.addCleanup(self.window.deleteLater)

    def test_maximized_window_is_restored_maximized(self):
        self.window.showMaximized()
        self.assertTrue(self.window.isMaximized())

        self.window.lifecycle.hide_window()
        self.assertTrue(self.window.isHidden())
        self.window.show_window()

        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.isMaximized())

    def test_normal_window_is_restored_normal(self):
        self.window.showNormal()

        self.window.lifecycle.hide_window()
        self.assertTrue(self.window.isHidden())
        self.window.show_window()

        self.assertTrue(self.window.isVisible())
        self.assertFalse(self.window.isMaximized())
        self.assertFalse(self.window.isFullScreen())

    def test_fullscreen_state_is_derived_from_qt(self):
        self.window.showFullScreen()
        self.assertTrue(self.window.isFullScreen())

        self.window.lifecycle.hide_window()
        self.window.show_window()

        self.assertTrue(self.window.isFullScreen())

    def test_window_never_hidden_is_shown_normal(self):
        self.window.restore_window()

        self.assertFalse(self.window.isMaximized())
        self.assertFalse(self.window.isFullScreen())

    def test_restoring_twice_keeps_the_state(self):
        self.window.showMaximized()

        for _ in range(2):
            self.window.lifecycle.hide_window()
            self.window.show_window()

        self.assertTrue(self.window.isMaximized())

    def test_state_is_captured_from_host_not_embedded_content(self):
        content = QMainWindow()
        self.addCleanup(content.deleteLater)
        content.showMaximized()

        lifecycle = WindowLifecycle(self.window, content)
        lifecycle.remember_window_state()
        lifecycle.restore_window()

        self.assertFalse(self.window.isMaximized())

    def test_save_preserves_existing_geometry_and_layout_keys(self):
        self.window.lifecycle.save_window_state()

        self.assertTrue(SettingsManager.contains("main/geometry"))
        self.assertTrue(SettingsManager.contains("main/windowState"))

    def test_request_close_uses_a_real_event_and_prepares_background(self):
        settings = SystemSettings()
        settings.confirm_on_close = False
        settings.keep_running_in_background = True
        self.window.show()

        self.window.lifecycle.request_close()

        self.assertTrue(self.window.isHidden())
        self.assertEqual(self.window.background_preparations, 1)

    def test_request_quit_bypasses_keep_running_in_background(self):
        settings = SystemSettings()
        settings.confirm_on_close = False
        settings.keep_running_in_background = True
        self.window.show()

        with patch(
            "zapzap.app.window_lifecycle.QApplication.instance"
        ) as application_instance:
            self.window.lifecycle.request_quit()

        application_instance.return_value.quit.assert_called_once_with()
        self.assertEqual(self.window.background_preparations, 0)

    def test_csr_host_exposes_the_application_contract_explicitly(self):
        content = _Content()
        host = ClientSideWindowHost(content)
        self.addCleanup(host.deleteLater)

        host.open_settings()

        self.assertIs(host.browser, content.browser)
        self.assertEqual(content.settings_opened, 1)
        self.assertNotIn("__getattr__", ClientSideWindowHost.__dict__)

    def test_csr_ctrl_w_hides_host_and_restores_normal_window(self):
        content = _MainWindowContent([])
        host = ClientSideWindowHost(content)
        self.addCleanup(host.deleteLater)
        host.showNormal()
        self.app.processEvents()

        content.actionHide.trigger()
        self.app.processEvents()

        self.assertTrue(host.isHidden())
        self.assertFalse(content.isHidden())
        self.assertIs(content.window(), host)

        host.show_window()
        self.app.processEvents()

        self.assertTrue(host.isVisible())
        self.assertFalse(host.isMaximized())
        self.assertFalse(host.isFullScreen())
        self.assertFalse(content.isHidden())
        self.assertIs(content.window(), host)

    def test_csr_ctrl_w_hides_host_and_restores_maximized_window(self):
        content = _MainWindowContent([])
        host = ClientSideWindowHost(content)
        self.addCleanup(host.deleteLater)
        host.showMaximized()
        self.app.processEvents()

        content.actionHide.trigger()
        self.app.processEvents()

        self.assertTrue(host.isHidden())
        self.assertFalse(content.isHidden())

        host.show_window()
        self.app.processEvents()

        self.assertTrue(host.isVisible())
        self.assertTrue(host.isMaximized())
        self.assertFalse(content.isHidden())
        self.assertIs(content.window(), host)

    def test_csr_ctrl_w_hides_host_and_restores_fullscreen_window(self):
        content = _MainWindowContent([])
        host = ClientSideWindowHost(content)
        self.addCleanup(host.deleteLater)
        host.showFullScreen()
        self.app.processEvents()

        content.actionHide.trigger()
        self.app.processEvents()

        self.assertTrue(host.isHidden())
        self.assertFalse(content.isHidden())

        host.show_window()
        self.app.processEvents()

        self.assertTrue(host.isVisible())
        self.assertTrue(host.isFullScreen())
        self.assertFalse(content.isHidden())
        self.assertIs(content.window(), host)

    def test_destroying_csr_host_does_not_query_it_from_embedded_content(self):
        hide_results = []
        content = _MainWindowContent(hide_results)
        host = ClientSideWindowHost(content)
        host.show()
        self.app.processEvents()

        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()

        self.assertTrue(hide_results)
        self.assertTrue(all(result is None for result in hide_results))

    def test_adwaita_close_button_uses_the_neutral_window_palette(self):
        settings = SimpleNamespace(
            csr_button_theme="adwaita",
            csr_buttons_direction="right",
            csr_show_minimize_button=True,
            csr_show_maximize_button=True,
        )
        content = QMainWindow()
        window = ClientSideWindow(content, settings)
        self.addCleanup(window.deleteLater)

        stylesheet = window.styleSheet()

        self.assertIn(
            """QPushButton#csrWindowCloseButton {
                background: palette(alternate-base);""",
            stylesheet,
        )
        self.assertIn(
            """QPushButton#csrWindowCloseButton:hover {
                background: palette(mid);""",
            stylesheet,
        )
        self.assertNotIn("palette(bright-text)", stylesheet)

        settings.csr_button_theme = "default"
        default_window = ClientSideWindow(QMainWindow(), settings)
        self.addCleanup(default_window.deleteLater)

        self.assertIn("palette(bright-text)", default_window.styleSheet())


if __name__ == "__main__":
    import unittest

    unittest.main()
