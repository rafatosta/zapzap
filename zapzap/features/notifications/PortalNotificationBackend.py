from __future__ import annotations

from typing import TYPE_CHECKING

from pathlib import Path
from uuid import uuid4

from PyQt6.QtCore import QObject, pyqtSlot, QByteArray, QMetaType
from PyQt6.QtDBus import (
    QDBusArgument,
    QDBusConnection,
    QDBusInterface,
    QDBusMessage,
    QDBusVariant,
)
from PyQt6.QtWebEngineCore import QWebEngineNotification
from PyQt6.QtWidgets import QApplication

from zapzap.features.notifications.FreedesktopNotificationBackend import IconRenderer
from zapzap.core.config.SettingsManager import SettingsManager

if TYPE_CHECKING:
    from zapzap.features.browser.webengine.WebView import WebView


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
        self._supports_icon_field = True
        self._supports_extra_fields = True

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
        notification_id = f"zapzap-page-{page.page_index}-{uuid4().hex}"

        self._notifications[notification_id] = notification
        self._pages[notification_id] = page

        base_payload = {
            "title": title,
            "body": message,
            "priority": "normal",
            "default-action": self.ACTION_FOCUS,
        }

        icon_field = {}
        if self._supports_icon_field:
            icon_data = self._get_icon_data(notification, title)
            if icon_data:
                icon_field = {
                    "icon": self._create_icon_arg(icon_data)
                }

        extra_fields = {}
        if self._supports_extra_fields:
            extra_fields = {
                "display-hint": ["show-as-new"],
                "category": "im.received",
            }

        attempts = []

        # First attempt: payload extended with icon and extra fields
        if icon_field and extra_fields:
            attempts.append((
                {**base_payload, **icon_field, **extra_fields},
                "[Portal] Notification payload extended with icon field and extra fields failed.",
            ))

        # Second attempt: payload extended with only icon field
        if icon_field:
            attempts.append((
                {**base_payload, **icon_field},
                "[Portal] Notification payload extended with icon field failed.",
            ))

        # Third attempt: payload extended with only extra fields
        if extra_fields:
            attempts.append((
                {**base_payload, **extra_fields},
                "[Portal] Notification payload extended with extra fields failed.",
            ))

        # Fourth attempt: minimal payload
        attempts.append((
            base_payload,
            "[Portal] Notification failed: {}",
        ))

        for payload, error_msg in attempts:
            reply = self.interface.call(
                "AddNotification",
                notification_id,
                self._build_dbus_variant_map(payload)
            )

            if (reply.type() != QDBusMessage.MessageType.ErrorMessage):
                notification.show()
                break

            print(error_msg.format(reply.errorMessage()))

        self._supports_icon_field = bool(icon_field) and icon_field.items() <= payload.items()
        self._supports_extra_fields = bool(extra_fields) and extra_fields.items() <= payload.items()


    def _build_dbus_variant_map(self, payload: dict):
        arg = QDBusArgument()
        arg.beginMap(
            QMetaType.Type.QString.value,
            QMetaType.fromName(b"QDBusVariant").id()
        )

        for key, value in payload.items():
            arg.beginMapEntry()
            arg.add(key)
            arg.add(QDBusVariant(value))
            arg.endMapEntry()

        arg.endMap()
        return arg


    def _create_icon_arg(self, data: bytes):
        arg = QDBusArgument()
        arg.beginStructure()
        # The recommended format for dynamic icon data is "file-descriptor".
        # However, PyQt6/QtDBus cannot currently marshal the required nested
        # variant(h) value for QDBusUnixFileDescriptor inside an (sv) structure.
        # Workaround: send icon data using the deprecated "bytes" format until
        # this is fixed upstream.
        arg.add("bytes")
        arg.add(QDBusVariant(QByteArray(data)))
        arg.endStructure()
        return arg


    def _get_icon_data(
        self,
        notification: QWebEngineNotification,
        title: str,
    ):
        try:
            icon_path = IconRenderer.default_icon()
            if SettingsManager.get("notification/show_photo", True):
                icon_path = IconRenderer.from_notification_icon(
                    notification.icon(),
                    title
                )

            if not icon_path:
                return None

            data = Path(icon_path).read_bytes()

            if not data:
                return None

            return data

        except Exception as e:
            print("[Portal] Failed to create notification icon:", e)
            return None


    # ---------------------------------------------------------
    # Action Handling
    # ---------------------------------------------------------

    @pyqtSlot(str, str, list)
    def _on_action_invoked(self, notification_id, action, parameters):
        if action != self.ACTION_FOCUS:
            return

        try:
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

            if page is not None:
                main_window.browser.switch_to_page(
                    page,
                    main_window.browser.page_buttons[page.page_index]
                )

            if notification:
                notification.click()

        except Exception as e:
            print("Portal ActionInvoked error:", e)
