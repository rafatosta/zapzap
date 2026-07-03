"""Controller for client-side rendered application windows."""

from gettext import gettext as _

from PyQt6.QtCore import QByteArray
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QWidget

from zapzap.controllers.QtoasterDonation import QtoasterDonation
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views import ClientSideRenderingView


class ClientSideRenderingController(ClientSideRenderingView):
    """Coordinates lifecycle behavior for the CSR window wrapper."""

    def __init__(self, inner_window: QWidget, enabled: bool = True):
        super().__init__(inner_window, enabled)

        if enabled and not SettingsManager.get("notification/donation_message", True):
            QtoasterDonation.showMessage(parent=self)

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

        from zapzap.services.SysTrayManager import SysTrayManager
        from zapzap.services.ThemeManager import ThemeManager
        SysTrayManager.start()
        ThemeManager.start()

    def closeEvent(self, event):
        self._save_window_state()

        if SettingsManager.get("system/confirm_on_close", False):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(_("Close ZapZap"))
            msg_box.setText(_("Are you sure you want to close?"))
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            cb = QCheckBox(_("Don't ask again"))
            msg_box.setCheckBox(cb)

            reply = msg_box.exec()
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

            if cb.isChecked():
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
