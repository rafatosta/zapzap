from __future__ import annotations

import os
from collections import OrderedDict

from PyQt6.QtCore import Qt, QSize, QStandardPaths
from PyQt6.QtGui import QPainter, QImage, QBrush, QPen
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.webengine import WebView
from zapzap.resources.TrayIcon import TrayIcon
from zapzap.services.SettingsManager import SettingsManager
from zapzap import __appname__

# -----------------------------------------------------------------------------
# Optional DBus imports (fail-safe)
# -----------------------------------------------------------------------------
try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
except Exception:
    dbus = None
    DBusGMainLoop = None


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
class DBusConnection:

    SERVICE = "org.freedesktop.Notifications"
    PATH = "/org/freedesktop/Notifications"
    IFACE = "org.freedesktop.Notifications"

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.interface = None
        self.available = False
        self._notifications: dict[int, DBusNotification] = {}

        self._init()

    def _init(self):
        if dbus is None:
            return

        try:
            if DBusGMainLoop:
                DBusGMainLoop(set_as_default=True)

            bus = dbus.SessionBus()
            proxy = bus.get_object(self.SERVICE, self.PATH)
            self.interface = dbus.Interface(proxy, self.IFACE)

            self.interface.connect_to_signal(
                "ActionInvoked", self._on_action_invoked
            )
            self.interface.connect_to_signal(
                "NotificationClosed", self._on_notification_closed
            )

            self.available = True
        except Exception:
            self.available = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def notify(self, notification: "DBusNotification") -> bool:
        if not self.available:
            return False

        nid = self.interface.Notify(
            self.app_name,
            notification.id,
            notification.icon,   # fallback
            notification.title,
            notification.body,
            notification.actions_list(),
            notification.hints,  # image-path aqui
            notification.timeout,
        )

        for old in list(self._notifications.values()):
            if notification.matches(old):
                self.close_notification(old)

        notification.id = int(nid)
        self._notifications[notification.id] = notification
        return True

    def close_notification(self, notification: "DBusNotification"):
        if notification.id and self.interface:
            try:
                self.interface.CloseNotification(notification.id)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # DBus callbacks
    # ------------------------------------------------------------------
    def _on_action_invoked(self, nid, action):
        nid = int(nid)
        action = str(action)
        if nid in self._notifications:
            self._notifications[nid].handle_action(action)

    def _on_notification_closed(self, nid, _reason):
        nid = int(nid)
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
        self.hints["urgency"] = dbus.Byte(value)

    def set_category(self, category: str):
        self.hints["category"] = category

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

    def handle_action(self, action: str):
        if action in self.actions:
            _, callback = self.actions[action]
            callback()

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
        notify.setIconPath(icon_path)  # 👈 ESSENCIAL

        def on_click():
            main = QApplication.instance().getWindow()
            main.show()
            main.raise_()
            main.activateWindow()
            main.browser.switch_to_page(
                page,
                main.browser.page_buttons[page.page_index],
            )
            notification.click()

        notify.add_action("default", "", on_click)

        try:
            notification.closed.connect(
                lambda: self._connection.close_notification(notify)
            )
        except Exception:
            pass

        self._connection.notify(notify)
