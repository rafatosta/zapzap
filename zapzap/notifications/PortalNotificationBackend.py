from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtDBus import (
    QDBusConnection,
    QDBusInterface,
    QDBusMessage,
)
from PyQt6.QtWebEngineCore import QWebEngineNotification
from PyQt6.QtWidgets import QApplication

from zapzap.webengine import WebView


class PortalNotificationBackend(QObject):
    ACTION_FOCUS = "focus"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bus = QDBusConnection.sessionBus()

        self.interface = QDBusInterface(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.Notification",
            self.bus
        )

        self._notifications = {}
        self._pages = {}

        # Assume suporte completo inicialmente
        self._supports_extended_fields = True

        self.bus.connect(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.Notification",
            "ActionInvoked",
            self._on_action_invoked
        )

    # ---------------------------------------------------------
    # Notify with Dynamic Fallback
    # ---------------------------------------------------------

    def notify(
        self,
        page: WebView,
        notification: QWebEngineNotification,
        title: str,
        message: str
    ):
        notification_id = f"zapzap-page-{page.page_index}"

        self._notifications[notification_id] = notification
        self._pages[notification_id] = page

        base_payload = {
            "title": title,
            "body": message,
            "priority": "normal",
            "default-action": self.ACTION_FOCUS,
            "default-action-target": page.page_index,
        }

        extended_fields = {
            "display-hint": "show-as-new",
            "category": "im.received",
        }

        # Primeira tentativa: payload completo
        if self._supports_extended_fields:
            payload = {**base_payload, **extended_fields}
        else:
            payload = base_payload

        reply = self.interface.call(
            "AddNotification",
            notification_id,
            payload
        )

        # -------------------------------------------------
        # Se falhar e ainda não testamos fallback:
        # -------------------------------------------------
        if (
            reply.type() == QDBusMessage.MessageType.ErrorMessage
            and self._supports_extended_fields
        ):
            print(
                "[Portal] Extended notification fields not supported. "
                "Falling back to minimal payload."
            )

            self._supports_extended_fields = False

            # Segunda tentativa sem campos extras
            reply = self.interface.call(
                "AddNotification",
                notification_id,
                base_payload
            )

        # -------------------------------------------------
        # Nunca quebrar o app
        # -------------------------------------------------
        if reply.type() == QDBusMessage.MessageType.ErrorMessage:
            print(
                "[Portal] Notification failed:",
                reply.errorMessage()
            )
            return  # não lançar exceção

        notification.show()

    # ---------------------------------------------------------
    # Action Handling
    # ---------------------------------------------------------

    @pyqtSlot(str, str, list)
    def _on_action_invoked(self, notification_id, action, parameters):

        if action != self.ACTION_FOCUS:
            return

        try:
            page_index = parameters[0]

            app = QApplication.instance()
            if not app:
                return

            main_window = app.getWindow()
            if not main_window:
                return

            main_window.show()
            main_window.raise_()
            main_window.activateWindow()

            notification = self._notifications.get(notification_id)
            page = self._pages.get(notification_id)

            main_window.browser.switch_to_page(
                page,
                main_window.browser.page_buttons[page_index]
            )

            if notification:
                notification.click()

        except Exception as e:
            print("Portal ActionInvoked error:", e)