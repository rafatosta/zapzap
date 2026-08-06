"""Top-level window lifecycle shared by native and client-side frames."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtWidgets import QApplication, QWidget

from zapzap.core.config.settings.system import SystemSettings
from zapzap.core.config.settings.window import WindowSettings
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager
from zapzap.ui.components.client_side_window import ClientSideWindow


class WindowLifecycle:
    """Coordinate persistence, close behavior and tray visibility."""

    NORMAL = "normal"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"

    def __init__(self, host: QWidget, content):
        self.host = host
        self.content = content
        self._system_settings = SystemSettings()
        self._window_settings = WindowSettings()
        self._restore_mode = self.NORMAL
        self._quit_requested = False

    def load_settings(self) -> None:
        self.host.restoreGeometry(self._window_settings.geometry)
        self.content.restoreState(self._window_settings.layout_state)
        SysTrayManager.start()

    def save_window_state(self) -> None:
        self._window_settings.geometry = self.host.saveGeometry()
        self._window_settings.layout_state = self.content.saveState()

    def request_close(self) -> None:
        self.host.close()

    def request_quit(self) -> None:
        """Close the host while bypassing background-only window behavior."""
        self._quit_requested = True
        self.host.close()

    def close_event(self, event) -> None:
        self.save_window_state()

        if self._system_settings.confirm_on_close:
            confirmed, dont_ask_again = AlertManager.question_with_checkbox(
                self.host,
                _("Close ZapZap"),
                _("Are you sure you want to close?"),
                _("Don't ask again"),
            )
            if not confirmed:
                self._quit_requested = False
                event.ignore()
                return

            if dont_ask_again:
                self._system_settings.confirm_on_close = False

        quit_requested = self._quit_requested
        self._quit_requested = False

        if (
            self._system_settings.keep_running_in_background
            and not quit_requested
        ):
            self.content.prepare_for_background()
            self.host.hide()
            event.ignore()
            return

        QApplication.instance().quit()

    def remember_window_state(self) -> None:
        if self.host.isFullScreen():
            self._restore_mode = self.FULLSCREEN
        elif self.host.isMaximized():
            self._restore_mode = self.MAXIMIZED
        else:
            self._restore_mode = self.NORMAL

    def restore_window(self) -> None:
        if self._restore_mode == self.FULLSCREEN:
            self.host.showFullScreen()
        elif self._restore_mode == self.MAXIMIZED:
            self.host.showMaximized()
        else:
            self.host.showNormal()

    def show_window(self) -> None:
        if self.host.isHidden():
            self.restore_window()
            QApplication.instance().setActiveWindow(self.host)
        elif not self.host.isActiveWindow():
            self.host.activateWindow()
            self.host.raise_()
        else:
            self.host.hide()


class ClientSideWindowHost(ClientSideWindow):
    """Top-level CSR host with an explicit application-window facade."""

    def __init__(self, inner_window):
        super().__init__(inner_window)
        self.lifecycle = WindowLifecycle(self, inner_window)
        inner_window.attach_window_host(self, self.lifecycle)

    @property
    def browser(self):
        return self.inner_window.browser

    @property
    def app_settings(self):
        return self.inner_window.app_settings

    def load_settings(self):
        self.lifecycle.load_settings()

    def save_window_state(self):
        self.lifecycle.save_window_state()

    def request_close(self):
        self.lifecycle.request_close()

    def request_quit(self):
        self.lifecycle.request_quit()

    def closeEvent(self, event):
        self.lifecycle.close_event(event)

    def hideEvent(self, event):
        self.lifecycle.remember_window_state()
        super().hideEvent(event)

    def restore_window(self):
        self.lifecycle.restore_window()

    def show_window(self):
        self.lifecycle.show_window()

    def open_settings(self):
        self.inner_window.open_settings()

    def open_donations(self):
        return self.inner_window.open_donations()

    def close_settings(self):
        self.inner_window.close_settings()

    def settings_menubar(self):
        self.inner_window.settings_menubar()

    def set_sidebar_visible(self, visible, animated=True, persist=True):
        self.inner_window.set_sidebar_visible(visible, animated, persist)

    def xdgOpenChat(self, url):
        self.inner_window.xdgOpenChat(url)
