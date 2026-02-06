from pathlib import Path
from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.controllers import WebView
from zapzap.services.SettingsManager import SettingsManager
from gettext import gettext as _
from zapzap import __appname__
""" from zapzap.notifications.FreedesktopNotificationBackend import (
    FreedesktopNotificationBackend
)
from zapzap.notifications.PortalNotificationBackend import (
    PortalNotificationBackend 
)
"""
from zapzap.notifications.DBusNotificationManager import DBusNotificationManager


""" def is_flatpak() -> bool:
    return Path("/.flatpak-info").exists() """


class NotificationService:

    _backend = None

    def __init__(self):

        """ if is_flatpak():
            if not NotificationService._backend:
                NotificationService._backend = PortalNotificationBackend()
        else:
            # self.backend = FreedesktopNotificationBackend()
            self.backend = None

        self.backend = NotificationService._backend """
        pass

    def notify(
        self,
        page: WebView,
        notification: QWebEngineNotification
    ):
        # =================================================
        # 1. Regras globais (app / usuário)
        # =================================================
        if not SettingsManager.get('notification/app', True):
            return

        if not SettingsManager.get(
            f'{str(page.user.id)}/notification', True
        ):
            return

        # =================================================
        # 2. Conteúdo (decisão global)
        # =================================================
        """ title = (
            notification.title()
            if SettingsManager.get('notification/show_name', True)
            else __appname__
        ) """

        """ message = (
            notification.message()
            if SettingsManager.get('notification/show_msg', True)
            else _('New message...')
        ) """

        # =================================================
        # 3. Delegação total ao backend
        # =================================================

        DBusNotificationManager.show(page, notification)

        """  if self.backend:  # flatpak
            self.backend.notify(
                page=page,
                notification=notification,
                title=title,
                message=message
            )
        else:  # desktop dbus
            DBusNotificationManager.show(page, notification) """
