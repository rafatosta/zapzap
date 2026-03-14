"""
Windows notification backend using Qt's built-in QSystemTrayIcon.showMessage().
No external dependencies required beyond PyQt6.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.webengine import WebView


class WindowsNotificationBackend:
    """
    Delivers notifications on Windows via the system tray message balloon.
    Clicking the balloon focuses the correct WhatsApp tab.
    """

    def available(self) -> bool:
        return True

    def notify(
        self,
        page: WebView,
        notification: QWebEngineNotification,
        title: str,
        message: str,
    ):
        from zapzap.services.SysTrayManager import SysTrayManager
        from PyQt6.QtWidgets import QApplication

        tray: QSystemTrayIcon = SysTrayManager.instance()._tray

        def _on_message_clicked():
            main = QApplication.instance().getWindow()
            if not main:
                return
            main.show()
            main.raise_()
            main.activateWindow()
            main.browser.switch_to_page(
                page,
                main.browser.page_buttons[page.page_index],
            )
            notification.click()

        # Disconnect any previous one-shot connection to avoid stacking
        try:
            tray.messageClicked.disconnect()
        except TypeError:
            pass

        tray.messageClicked.connect(_on_message_clicked)
        tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 4000)
        notification.show()
