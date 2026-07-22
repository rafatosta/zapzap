"""Controller for client-side rendered application windows."""

from gettext import gettext as _

from PyQt6.QtCore import QByteArray
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget

from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.donation.controller import DonationController
from zapzap.ui.main_window.client_side_rendering_view import ClientSideRenderingView


class ClientSideRenderingController(ClientSideRenderingView):
    """Coordinates lifecycle behavior for the CSR window wrapper."""

    def __init__(self, inner_window: QWidget, enabled: bool = True):
        super().__init__(inner_window, enabled)

        if enabled and DonationController.should_show():
            DonationController.showMessage(parent=self)

    def load_settings(self):
        """Restore window state in CSR mode and start global services."""
        if self.enabled:
            self.restoreGeometry(SettingsManager.get(
                "main/geometry", QByteArray()))
            self.inner_window.restoreState(
                SettingsManager.get("main/windowState", QByteArray()))
        else:
            self.inner_window.load_settings()
            return

        from zapzap.features.tray.sys_tray_manager import SysTrayManager
        from zapzap.core.theme.theme_manager import ThemeManager
        SysTrayManager.start()
        ThemeManager.start()

    def closeEvent(self, event):
        self._save_window_state()

        if SettingsManager.get("system/confirm_on_close", False):
            confirmed, dont_ask_again = AlertManager.question_with_checkbox(
                self,
                _("Close ZapZap"),
                _("Are you sure you want to close?"),
                _("Don't ask again"),
            )
            if not confirmed:
                event.ignore()
                return

            if dont_ask_again:
                SettingsManager.set("system/confirm_on_close", False)

        if not SettingsManager.get("system/quit_in_close", False) and event:
            self._prepare_for_background(event)
        else:
            QApplication.instance().quit()

    def _save_window_state(self):
        SettingsManager.set("main/geometry", self.saveGeometry())
        SettingsManager.set("main/windowState", self.saveState())

    def _prepare_for_background(self, event):
        if self.inner_window.app_settings:
            self.inner_window.close_settings()

        self.inner_window.browser.close_conversations()
        self.hide()
        event.ignore()

    def show_window(self):
        if self.isHidden():
            if self.inner_window.is_fullscreen:
                self.showFullScreen()
            else:
                self.showNormal()
            QApplication.instance().setActiveWindow(self)
        elif not self.isActiveWindow():
            self.activateWindow()
            self.raise_()
        else:
            self.hide()

    def hideEvent(self, event):
        super().hideEvent(event)

    def __getattr__(self, name):
        return getattr(self.inner_window, name)
