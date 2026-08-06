from __future__ import annotations

from typing import TYPE_CHECKING

import os
from collections import OrderedDict

from PyQt6.QtCore import (
    QMetaType,
    QObject,
    QStandardPaths,
    QSize,
    Qt,
    QVariant,
    pyqtSlot,
)
from PyQt6.QtDBus import (
    QDBusArgument,
    QDBusConnection as QtDBusConnection,
    QDBusInterface,
    QDBusMessage,
    QDBusVariant,
)
from PyQt6.QtGui import QPainter, QImage, QBrush, QPen
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.notifications.window_activation import activate_window
from zapzap import __appname__

if TYPE_CHECKING:
    from zapzap.features.browser.web.web_view import WebView

# -----------------------------------------------------------------------------
# Domain
# -----------------------------------------------------------------------------
class Urgency:
    LOW, NORMAL, CRITICAL = range(3)


# -----------------------------------------------------------------------------
# Infrastructure: Icon rendering (lógica ORIGINAL preservada)
# -----------------------------------------------------------------------------
class IconRenderer:

    @staticmethod
    def temp_dir() -> str:
        path = os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            ),
            "tmp"
        )
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def from_notification_icon(cls, icon, title: str) -> str:
        """
        Desenha avatar circular usando QPainter e salva como PNG.
        Retorna string vazia em caso de falha (quem chama faz fallback).
        """
        try:
            path = os.path.join(cls.temp_dir(), f"{title}.png")

            output_image = QImage(
                icon.width(),
                icon.height(),
                QImage.Format.Format_ARGB32
            )
            output_image.fill(Qt.GlobalColor.transparent)

            painter = QPainter(output_image)
            painter.setBrush(QBrush(icon))
            painter.setPen(QPen(Qt.GlobalColor.darkGray))
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.drawRoundedRect(
                0,
                0,
                icon.width(),
                icon.height(),
                icon.width() // 2,
                icon.height() // 2,
            )
            painter.end()

            if output_image.save(path):
                return path

        except Exception:
            pass

        return ""

    @classmethod
    def default_icon(cls) -> str:
        """
        Fallback original: ícone do Tray.
        """
        try:
            icon = TrayIcon.getIcon()
            pixmap = icon.pixmap(QSize(128, 128))
            path = os.path.join(cls.temp_dir(), "com.rtosta.zapzap.png")
            pixmap.save(path)
            return path
        except Exception:
            return ""


# -----------------------------------------------------------------------------
# Infrastructure: DBus connection
# -----------------------------------------------------------------------------
class DBusConnection(QObject):

    SERVICE = "org.freedesktop.Notifications"
    PATH = "/org/freedesktop/Notifications"
    IFACE = "org.freedesktop.Notifications"

    _SIGNALS = (
        ("ActionInvoked", "us", "_on_action_invoked"),
        ("ActivationToken", "us", "_on_activation_token"),
        ("NotificationClosed", "uu", "_on_notification_closed"),
    )

    def __init__(self, app_name: str, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.bus = QtDBusConnection.sessionBus()
        self.interface = None
        self.available = False
        self._signals_connected = False
        self._notifications: dict[int, DBusNotification] = {}
        self._activation_tokens: dict[int, str] = {}

        self._init()

    def _init(self):
        self.interface = None
        self.available = False

        if not self.bus.isConnected():
            return

        interface = QDBusInterface(
            self.SERVICE,
            self.PATH,
            self.IFACE,
            self.bus,
        )
        if not interface.isValid():
            return

        if not self._signals_connected and not self._connect_signals():
            return

        self.interface = interface
        self.available = True

    def _connect_signals(self) -> bool:
        connected = []
        for name, signature, callback_name in self._SIGNALS:
            callback = getattr(self, callback_name)
            if not self.bus.connect(
                self.SERVICE,
                self.PATH,
                self.IFACE,
                name,
                signature,
                callback,
            ):
                for old_name, old_signature, old_callback in connected:
                    self.bus.disconnect(
                        self.SERVICE,
                        self.PATH,
                        self.IFACE,
                        old_name,
                        old_signature,
                        old_callback,
                    )
                return False
            connected.append((name, signature, callback))

        self._signals_connected = True
        return True

    def _mark_unavailable(self):
        self.available = False
        self.interface = None

    @staticmethod
    def _build_hints(values: dict) -> QDBusArgument:
        hints = QDBusArgument()
        hints.beginMap(
            QMetaType.Type.QString.value,
            QMetaType.fromName(b"QDBusVariant").id(),
        )

        for key, value in values.items():
            hints.beginMapEntry()
            hints.add(key)
            hints.add(QDBusVariant(value))
            hints.endMapEntry()

        hints.endMap()
        return hints

    @staticmethod
    def _build_string_array(values: list[str]) -> QDBusArgument:
        strings = QDBusArgument()
        strings.beginArray(QMetaType.Type.QString.value)
        for value in values:
            strings.add(value)
        strings.endArray()
        return strings

    @staticmethod
    def _dbus_uint(value: int) -> QVariant:
        value = int(value)
        if not 0 <= value <= 0xFFFFFFFF:
            raise ValueError(f"Invalid D-Bus UINT32 value: {value}")

        unsigned = QVariant(value)
        if not unsigned.convert(QMetaType(QMetaType.Type.UInt.value)):
            raise ValueError(f"Invalid D-Bus UINT32 value: {value}")
        return unsigned

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def notify(self, notification: "DBusNotification") -> bool:
        if not self.available or self.interface is None:
            # Notification daemons can restart mid-session.
            # Retry connection lazily without crashing the app.
            self._init()

        if not self.available or self.interface is None:
            return False

        try:
            reply = self.interface.call(
                "Notify",
                self.app_name,
                self._dbus_uint(notification.id),
                notification.icon,   # fallback
                notification.title,
                notification.body,
                self._build_string_array(notification.actions_list()),
                self._build_hints(notification.hints),
                notification.timeout,
            )
        except Exception:
            self._mark_unavailable()
            return False

        if reply.type() == QDBusMessage.MessageType.ErrorMessage:
            self._mark_unavailable()
            return False

        arguments = reply.arguments()
        if not arguments:
            self._mark_unavailable()
            return False

        for old in list(self._notifications.values()):
            if notification.matches(old):
                self.close_notification(old)

        notification.id = int(arguments[0])
        self._notifications[notification.id] = notification
        return True

    def close_notification(self, notification: "DBusNotification"):
        if notification.id and self.interface:
            try:
                reply = self.interface.call(
                    "CloseNotification",
                    self._dbus_uint(notification.id),
                )
                if reply.type() == QDBusMessage.MessageType.ErrorMessage:
                    self._mark_unavailable()
            except Exception:
                self._mark_unavailable()

    # ------------------------------------------------------------------
    # DBus callbacks
    # ------------------------------------------------------------------
    @pyqtSlot("uint", str)
    def _on_activation_token(self, nid, activation_token):
        nid = int(nid)
        activation_token = str(activation_token)
        if nid in self._notifications and activation_token:
            self._activation_tokens[nid] = activation_token

    @pyqtSlot("uint", str)
    def _on_action_invoked(self, nid, action):
        nid = int(nid)
        action = str(action)
        if nid in self._notifications:
            token = self._activation_tokens.pop(nid, None)
            self._notifications[nid].handle_action(action, token)

    @pyqtSlot("uint", "uint")
    def _on_notification_closed(self, nid, _reason):
        nid = int(nid)
        self._activation_tokens.pop(nid, None)
        if nid in self._notifications:
            self._notifications[nid].handle_closed()
            del self._notifications[nid]


# -----------------------------------------------------------------------------
# Domain: Notification (PURO)
# -----------------------------------------------------------------------------
class DBusNotification:

    def __init__(
        self,
        title: str,
        body: str,
        icon: str,
        timeout: int,
        web_notification: QWebEngineNotification | None = None,
    ):
        self.id = 0
        self.title = title
        self.body = body
        self.icon = icon
        self.timeout = timeout
        self.web_notification = web_notification

        self.hints: dict = {}
        self.actions: OrderedDict[str, tuple] = OrderedDict()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def set_urgency(self, value: int):
        value = int(value)
        if not 0 <= value <= 255:
            raise ValueError(f"Invalid notification urgency: {value}")

        urgency = QVariant(value)
        if not urgency.convert(QMetaType(QMetaType.Type.UChar.value)):
            raise ValueError(f"Invalid notification urgency: {value}")
        self.hints["urgency"] = urgency

    def set_category(self, category: str):
        self.hints["category"] = category

    def set_suppress_sound(self, suppress: bool):
        """Ask the server not to play its alert sound for this notification."""
        self.hints["suppress-sound"] = bool(suppress)

    def setIconPath(self, icon_path: str):
        """
        Necessário para ícones dinâmicos (avatar).
        """
        self.hints["image-path"] = icon_path

    def add_action(self, key: str, label: str, callback):
        self.actions[key] = (label, callback)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def actions_list(self) -> list[str]:
        arr = []
        for key, (label, _) in self.actions.items():
            arr.extend([key, label])
        return arr

    def handle_action(
        self,
        action: str,
        activation_token: str | None = None,
    ):
        if action in self.actions:
            _, callback = self.actions[action]
            callback(activation_token)

    def handle_closed(self):
        pass

    def matches(self, other: "DBusNotification") -> bool:
        if not self.web_notification or not other.web_notification:
            return False
        return self.web_notification.matches(other.web_notification)


# -----------------------------------------------------------------------------
# Backend (contrato compatível com PortalNotificationBackend)
# -----------------------------------------------------------------------------
class FreedesktopNotificationBackend:

    def __init__(self):
        self._connection = DBusConnection(__appname__)

    def available(self) -> bool:
        return self._connection.available

    def notify(
        self,
        page: WebView,
        notification: QWebEngineNotification,
        title: str,
        message: str,
    ):
        if not self.available():
            return

        # -------------------------------------------------
        # ÍCONE (lógica original preservada)
        # -------------------------------------------------
        icon_path = ""

        if SettingsManager.get("notification/show_photo", True):
            icon_path = IconRenderer.from_notification_icon(
                notification.icon(),
                title,
            )

        if not icon_path:
            icon_path = IconRenderer.default_icon()

        notify = DBusNotification(
            title=title,
            body=message,
            icon=icon_path,   # fallback
            timeout=3000,
            web_notification=notification,
        )

        notify.set_urgency(Urgency.NORMAL)
        notify.set_category("im.received")
        notify.set_suppress_sound(
            not SettingsManager.get("notification/sound", True)
        )
        notify.setIconPath(icon_path)  # 👈 ESSENCIAL

        def on_click(activation_token=None):
            main = QApplication.instance().getWindow()
            activate_window(main, activation_token)
            main.browser.activate_account(page.user.id)
            notification.click()

        notify.add_action("default", "", on_click)

        try:
            notification.closed.connect(
                lambda: self._connection.close_notification(notify)
            )
        except Exception:
            pass

        self._connection.notify(notify)
