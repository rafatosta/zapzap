from pathlib import Path
from gettext import gettext as _
import logging

from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.webengine import WebView
from zapzap.services.SettingsManager import SettingsManager
from zapzap import __appname__

from zapzap.notifications.PortalNotificationBackend import (
    PortalNotificationBackend
)
from zapzap.notifications.FreedesktopNotificationBackend import (
    FreedesktopNotificationBackend
)

logger = logging.getLogger(__name__)


def is_flatpak() -> bool:
    return Path("/.flatpak-info").exists()


class NotificationService:
    """
    Fachada única para notificações.

    Decide o backend (Portal / Freedesktop / None)
    e delega completamente a ele.
    """

    _backend = None

    def __init__(self):
        if NotificationService._backend is None:
            NotificationService._backend = self._select_backend()

        self.backend = NotificationService._backend

    # ------------------------------------------------------------------
    # Backend selection
    # ------------------------------------------------------------------
    def _select_backend(self):
        from zapzap.platform import IS_WINDOWS
        if IS_WINDOWS:
            from zapzap.notifications.WindowsNotificationBackend import (
                WindowsNotificationBackend,
            )
            return WindowsNotificationBackend()

        if is_flatpak():
            return PortalNotificationBackend()

        backend = FreedesktopNotificationBackend()
        return backend if backend.available() else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def notify(
        self,
        page: WebView,
        notification: QWebEngineNotification
    ):
        # =================================================
        # 1. Regras globais (app / usuário)
        # =================================================
        if not SettingsManager.get("notification/app", True):
            return

        if not SettingsManager.get(
            f"{page.user.id}/notification", True
        ):
            return

        if not self.backend:
            return

        # =================================================
        # 2. Conteúdo (decisão global)
        # =================================================
        title = (
            notification.title()
            if SettingsManager.get("notification/show_name", True)
            else __appname__
        )

        message = (
            notification.message()
            if SettingsManager.get("notification/show_msg", True)
            else _("New message...")
        )

        # =================================================
        # 3. Delegação total ao backend
        # =================================================
        try:
            self.backend.notify(
                page=page,
                notification=notification,
                title=title,
                message=message,
            )
        except Exception:
            # Notification failures must never crash the app.
            logger.warning(
                "Notification backend failed; dropping notification",
                exc_info=True,
            )
