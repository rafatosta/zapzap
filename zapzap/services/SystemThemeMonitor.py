from __future__ import annotations

from typing import Any
from typing import cast

from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtDBus import QDBusConnection
from PyQt6.QtDBus import QDBusInterface
from PyQt6.QtDBus import QDBusMessage
from PyQt6.QtDBus import QDBusVariant
from PyQt6.QtGui import QStyleHints
from PyQt6.QtWidgets import QApplication


class SystemThemeMonitor(QObject):
    """Monitors system color scheme changes.

    Uses XDG Desktop Portal when available. Falls back to Qt style hints on
    platforms or environments where the portal is unavailable.
    """
    SERVICE = "org.freedesktop.portal.Desktop"
    PATH = "/org/freedesktop/portal/desktop"
    INTERFACE = "org.freedesktop.portal.Settings"
    NAMESPACE = "org.freedesktop.appearance"
    KEY = "color-scheme"

    color_scheme_changed = pyqtSignal(Qt.ColorScheme)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._enabled = False
        self._portal_monitoring = False
        self._qt_style_hints_monitoring = False
        self._current_color_scheme = type(self)._get_current_color_scheme()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)

        if self._enabled == enabled:
            return

        if enabled:
            started = self._start_monitor()
            if not started:
                return
        else:
            self._stop_monitor()

        self._enabled = enabled

    # === Public methods === #
    def get_current_color_scheme(self) -> Qt.ColorScheme:
        return self._current_color_scheme

    # === Common private methods === #
    def _start_monitor(self) -> bool:
        if self._portal_start_monitor():
            return True

        return self._qt_style_hints_start_monitor()

    def _stop_monitor(self) -> None:
        self._portal_stop_monitor()
        self._qt_style_hints_stop_monitor()

    def _report_color_scheme_changed(self, color_scheme: Qt.ColorScheme) -> None:
        if color_scheme == self._current_color_scheme:
            return

        self._current_color_scheme = color_scheme
        self.color_scheme_changed.emit(color_scheme)

    @classmethod
    def _get_current_color_scheme(cls) -> Qt.ColorScheme:
        color_scheme = cls._portal_get_current_color_scheme()

        if color_scheme in (Qt.ColorScheme.Dark, Qt.ColorScheme.Light):
            return color_scheme

        return cls._qt_style_hints_get_current_color_scheme()

    # === Portal private methods === #
    def _portal_start_monitor(self) -> bool:
        if self._portal_monitoring:
            return True

        bus = QDBusConnection.sessionBus()

        if not bus.isConnected():
            return False

        self._portal_monitoring = bus.connect(
            "",
            type(self).PATH,
            type(self).INTERFACE,
            "SettingChanged",
            self._portal_color_scheme_changed,
        )

        return self._portal_monitoring

    def _portal_stop_monitor(self) -> None:
        if not self._portal_monitoring:
            return

        disconnected = QDBusConnection.sessionBus().disconnect(
            "",
            type(self).PATH,
            type(self).INTERFACE,
            "SettingChanged",
            self._portal_color_scheme_changed,
        )

        if disconnected:
            self._portal_monitoring = False

    @classmethod
    def _portal_get_current_color_scheme(cls) -> Qt.ColorScheme:
        iface = QDBusInterface(
            cls.SERVICE,
            cls.PATH,
            cls.INTERFACE,
            QDBusConnection.sessionBus(),
        )

        reply = iface.call("Read", cls.NAMESPACE, cls.KEY)

        if reply.type() == QDBusMessage.MessageType.ErrorMessage:
            return Qt.ColorScheme.Unknown

        args = reply.arguments()
        if not args:
            return Qt.ColorScheme.Unknown

        return cls._portal_get_color_scheme_from_value(args[0])

    @pyqtSlot(str, str, QDBusVariant)
    def _portal_color_scheme_changed(
        self,
        namespace: str,
        key: str,
        value: QDBusVariant,
    ) -> None:
        if namespace != type(self).NAMESPACE:
            return

        if key != type(self).KEY:
            return

        color_scheme = type(self)._portal_get_color_scheme_from_value(value)
        if color_scheme == Qt.ColorScheme.Unknown:
            color_scheme = type(self)._portal_get_current_color_scheme()

        self._report_color_scheme_changed(color_scheme)

    @classmethod
    def _portal_get_color_scheme_from_value(cls, value: Any) -> Qt.ColorScheme:
        while isinstance(value, QDBusVariant):
            value = value.variant()

        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 0

        return {
            0: Qt.ColorScheme.Unknown,
            1: Qt.ColorScheme.Dark,
            2: Qt.ColorScheme.Light,
        }.get(value, Qt.ColorScheme.Unknown)

    # === Qt style hints private methods === #
    @classmethod
    def _qt_style_hints_get_style_hints(cls) -> QStyleHints | None:
        app = cast(QApplication | None, QApplication.instance())
        return app.styleHints() if app else None

    def _qt_style_hints_start_monitor(self) -> bool:
        if self._qt_style_hints_monitoring:
            return True

        style_hints = type(self)._qt_style_hints_get_style_hints()
        if style_hints is None:
            return False

        style_hints.colorSchemeChanged.connect(
            self._qt_style_hints_color_scheme_changed
        )

        self._qt_style_hints_monitoring = True
        return True

    def _qt_style_hints_stop_monitor(self) -> None:
        if not self._qt_style_hints_monitoring:
            return

        style_hints = type(self)._qt_style_hints_get_style_hints()
        if style_hints is None:
            return

        try:
            style_hints.colorSchemeChanged.disconnect(
                self._qt_style_hints_color_scheme_changed
            )
        except TypeError:
            pass

        self._qt_style_hints_monitoring = False

    @classmethod
    def _qt_style_hints_get_current_color_scheme(cls) -> Qt.ColorScheme:
        style_hints = cls._qt_style_hints_get_style_hints()
        if not style_hints:
            return Qt.ColorScheme.Unknown

        color_scheme = style_hints.colorScheme()
        if color_scheme not in (Qt.ColorScheme.Light, Qt.ColorScheme.Dark):
            return Qt.ColorScheme.Unknown

        return color_scheme

    def _qt_style_hints_color_scheme_changed(self, new_system_color_scheme: Qt.ColorScheme) -> None:
        self._report_color_scheme_changed(new_system_color_scheme)