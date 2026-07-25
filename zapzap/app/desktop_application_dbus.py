"""org.freedesktop.Application integration for desktop activation."""

from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, pyqtClassInfo, pyqtSignal, pyqtSlot
from PyQt6.QtDBus import QDBusAbstractAdaptor, QDBusConnection

from zapzap import __desktopid__
from zapzap.features.notifications.window_activation import (
    activate_window,
    platform_activation_token,
)


logger = logging.getLogger(__name__)


@pyqtClassInfo("D-Bus Interface", "org.freedesktop.Application")
class FreedesktopApplicationAdaptor(QDBusAbstractAdaptor):
    activationRequested = pyqtSignal(object)
    openRequested = pyqtSignal(list)

    @pyqtSlot("QVariantMap")
    def Activate(self, platform_data):
        self.activationRequested.emit(
            platform_activation_token(platform_data)
        )

    @pyqtSlot("QStringList", "QVariantMap")
    def Open(self, uris, platform_data):
        self.activationRequested.emit(
            platform_activation_token(platform_data)
        )
        self.openRequested.emit(list(uris))

    @pyqtSlot(str, "QVariantList", "QVariantMap")
    def ActivateAction(self, _action_name, _parameters, platform_data):
        self.activationRequested.emit(
            platform_activation_token(platform_data)
        )


class DesktopApplicationDBus(QObject):
    """Own the desktop application ID while the primary instance is running."""

    def __init__(self, application, parent=None):
        super().__init__(parent or application)
        self._application = application
        self._bus = QDBusConnection.sessionBus()
        self._object_path = f"/{__desktopid__.replace('.', '/')}"
        self._registered_service = False
        self._registered_object = False

        self.adaptor = FreedesktopApplicationAdaptor(self)
        self.adaptor.activationRequested.connect(self._activate)
        self.adaptor.openRequested.connect(self._open_uris)

    def start(self) -> bool:
        self._registered_service = self._bus.registerService(__desktopid__)
        if not self._registered_service:
            logger.warning(
                "Could not own D-Bus application name %s",
                __desktopid__,
            )
            return False

        self._registered_object = self._bus.registerObject(
            self._object_path,
            self,
            QDBusConnection.RegisterOption.ExportAdaptors,
        )
        if not self._registered_object:
            self._bus.unregisterService(__desktopid__)
            self._registered_service = False
            logger.warning(
                "Could not export D-Bus application object %s",
                self._object_path,
            )
            return False

        return True

    def stop(self):
        if self._registered_object:
            self._bus.unregisterObject(self._object_path)
            self._registered_object = False
        if self._registered_service:
            self._bus.unregisterService(__desktopid__)
            self._registered_service = False

    def _activate(self, activation_token=None):
        window = self._application.getWindow()
        if window is not None:
            activate_window(window, activation_token)

    def _open_uris(self, uris):
        window = self._application.getWindow()
        if window is None:
            return

        for uri in uris:
            window.xdgOpenChat(uri)
