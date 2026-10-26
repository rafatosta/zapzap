"""Detect the desktop Do Not Disturb state on Linux.

Two sources are watched, and DND is active when any available one reports it:

* ``org.freedesktop.Notifications.Inhibited`` (KDE Plasma and any other
  notification server implementing the property);
* the portal setting ``org.gnome.desktop.notifications/show-banners``
  (GNOME). Whether the portal exposes this key is unverified.
"""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtDBus import (
    QDBus,
    QDBusConnection,
    QDBusMessage,
    QDBusVariant,
)

from zapzap.core.platform import IS_MAC, IS_WINDOWS

logger = logging.getLogger(__name__)

_NOTIFICATIONS_SERVICE = "org.freedesktop.Notifications"
_NOTIFICATIONS_PATH = "/org/freedesktop/Notifications"
_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"

_PORTAL_SERVICE = "org.freedesktop.portal.Desktop"
_PORTAL_PATH = "/org/freedesktop/portal/desktop"
_PORTAL_SETTINGS_INTERFACE = "org.freedesktop.portal.Settings"
_GNOME_NAMESPACE = "org.gnome.desktop.notifications"
_GNOME_KEY = "show-banners"

_DBUS_SERVICE = "org.freedesktop.DBus"
_DBUS_PATH = "/org/freedesktop/DBus"

# Readers run on the GUI thread; never wait for a slow service for long.
_CALL_TIMEOUT_MS = 1000


def _unwrap(value: Any) -> Any:
    while isinstance(value, QDBusVariant):
        value = value.variant()
    return value


class DoNotDisturbMonitor(QObject):
    """Track whether the desktop is in Do Not Disturb mode."""

    changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inhibited = False
        self._banners_hidden = False
        self._started = False

    @property
    def active(self) -> bool:
        return self._inhibited or self._banners_hidden

    def start(self) -> None:
        """Read the current state and subscribe to changes; idempotent."""
        if self._started or IS_WINDOWS or IS_MAC:
            return
        bus = QDBusConnection.sessionBus()
        if not bus.isConnected():
            logger.debug("Do Not Disturb unavailable: no session bus")
            return
        self._started = True

        subscriptions = (
            (
                _NOTIFICATIONS_SERVICE,
                _NOTIFICATIONS_PATH,
                _PROPERTIES_INTERFACE,
                "PropertiesChanged",
                self._properties_changed,
            ),
            (
                "",
                _PORTAL_PATH,
                _PORTAL_SETTINGS_INTERFACE,
                "SettingChanged",
                self._portal_setting_changed,
            ),
            (
                _DBUS_SERVICE,
                _DBUS_PATH,
                _DBUS_SERVICE,
                "NameOwnerChanged",
                self._name_owner_changed,
            ),
        )
        for subscription in subscriptions:
            if not bus.connect(*subscription):
                logger.warning(
                    "Could not subscribe to %s; Do Not Disturb changes may "
                    "be missed",
                    subscription[3],
                )
        self._inhibited = self._read_inhibited()
        self._banners_hidden = self._read_banners_hidden()

    # === Readers === #
    @staticmethod
    def _call(service: str, path: str, interface: str, method: str, *args):
        message = QDBusMessage.createMethodCall(service, path, interface, method)
        message.setArguments(list(args))
        return QDBusConnection.sessionBus().call(
            message, QDBus.CallMode.Block, _CALL_TIMEOUT_MS
        )

    def _read_inhibited(self) -> bool:
        reply = self._call(
            _NOTIFICATIONS_SERVICE,
            _NOTIFICATIONS_PATH,
            _PROPERTIES_INTERFACE,
            "Get",
            _NOTIFICATIONS_SERVICE,
            "Inhibited",
        )
        return self._bool_from_reply(reply, "Inhibited", default=False)

    def _read_banners_hidden(self) -> bool:
        reply = self._call(
            _PORTAL_SERVICE,
            _PORTAL_PATH,
            _PORTAL_SETTINGS_INTERFACE,
            "Read",
            _GNOME_NAMESPACE,
            _GNOME_KEY,
        )
        # show-banners is true when banners are shown, so hidden is its inverse.
        return not self._bool_from_reply(reply, _GNOME_KEY, default=True)

    @staticmethod
    def _bool_from_reply(reply: QDBusMessage, name: str, *, default: bool) -> bool:
        """Return a boolean from a D-Bus reply, or ``default`` if unavailable."""
        if reply.type() != QDBusMessage.MessageType.ReplyMessage:
            logger.debug("Do Not Disturb source %s unavailable", name)
            return default
        args = reply.arguments()
        if not args:
            return default
        value = _unwrap(args[0])
        return value if isinstance(value, bool) else default

    # === Signal slots === #
    @pyqtSlot(QDBusMessage)
    def _properties_changed(self, message: QDBusMessage) -> None:
        args = message.arguments()
        if not args or args[0] != _NOTIFICATIONS_SERVICE:
            return
        self._update(inhibited=self._read_inhibited())

    @pyqtSlot(str, str, str)
    def _name_owner_changed(
        self, name: str, _old_owner: str, new_owner: str
    ) -> None:
        """Re-read after a server restart; a vanished server cannot inhibit."""
        if name != _NOTIFICATIONS_SERVICE:
            return
        self._update(inhibited=self._read_inhibited() if new_owner else False)

    @pyqtSlot(str, str, QDBusVariant)
    def _portal_setting_changed(
        self, namespace: str, key: str, value: QDBusVariant
    ) -> None:
        if namespace != _GNOME_NAMESPACE or key != _GNOME_KEY:
            return
        shown = _unwrap(value)
        if isinstance(shown, bool):
            self._update(banners_hidden=not shown)

    def _update(
        self,
        *,
        inhibited: bool | None = None,
        banners_hidden: bool | None = None,
    ) -> None:
        before = self.active
        if inhibited is not None:
            self._inhibited = inhibited
        if banners_hidden is not None:
            self._banners_hidden = banners_hidden
        if self.active != before:
            self.changed.emit(self.active)
