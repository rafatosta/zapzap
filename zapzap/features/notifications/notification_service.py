from __future__ import annotations

from typing import TYPE_CHECKING

from pathlib import Path
from gettext import gettext as _
import logging

from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.core.config.settings.notifications import NotificationSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap import __appname__

from zapzap.features.notifications.portal_notification_backend import (
    PortalNotificationBackend
)
from zapzap.features.notifications.freedesktop_notification_backend import (
    FreedesktopNotificationBackend
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from zapzap.features.browser.web.web_view import WebView


def is_flatpak() -> bool:
    return Path("/.flatpak-info").exists()


# WhatsApp addresses every chat with a JID, "user@domain", whose domain says
# what kind of chat it is: "c.us" or "lid" for a person, "g.us" for a group,
# "newsletter" for a Channel, "broadcast" for status. WhatsApp Web publishes
# that JID as the tag of the notification it raises, and the tag is the only
# field QWebEngineNotification carries that identifies where the message came
# from: there is no access to the data or silent options of the underlying web
# notification.
#
# The tag is the chat JID on its own, except that some notifications identify
# a single message instead, joining the fields of a message key with "_". Both
# forms are read the same way, by looking at the domain of every JID in the
# tag. If WhatsApp Web changes the format, this is written in its
# WAWebMsgNotification, WAWebBaseNotificationBanner and WAWebWid modules.
CHANNEL_JID_DOMAIN = "newsletter"


def _jid_domains(tag: str) -> list[str]:
    """The domain of every JID the tag is built from, lowercased."""
    domains = []
    for token in tag.lower().split("_"):
        user, separator, domain = token.partition("@")
        if separator and user and domain:
            domains.append(domain)
    return domains


def is_channel_notification(notification: QWebEngineNotification) -> bool:
    """Whether a notification announces a post from a WhatsApp Channel.

    Only a tag built entirely out of Channel JIDs counts, so a tag that names
    no chat, that WhatsApp Web publishes in an unknown format, or that names a
    person alongside a Channel, leaves the notification visible instead of
    silently hiding a real message.
    """
    domains = _jid_domains(notification.tag() or "")
    return bool(domains) and all(
        domain == CHANNEL_JID_DOMAIN for domain in domains
    )


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
        self.settings = NotificationSettings()

    # ------------------------------------------------------------------
    # Backend selection
    # ------------------------------------------------------------------
    def _select_backend(self):
        from zapzap.core.platform import IS_WINDOWS, IS_MAC
        if IS_WINDOWS:
            from zapzap.features.notifications.windows_notification_backend import (
                WindowsNotificationBackend,
            )
            return WindowsNotificationBackend()

        if IS_MAC:
            from zapzap.features.notifications.macos_notification_backend import (
                MacosNotificationBackend,
            )
            return MacosNotificationBackend()

        if is_flatpak():
            return PortalNotificationBackend()

        backend = FreedesktopNotificationBackend()
        return backend if backend.available() else None

    @classmethod
    def shutdown(cls):
        """Withdraw active notifications before the application exits."""
        backend = cls._backend
        if backend is None:
            return

        close_all = getattr(backend, "close_all", None)
        if close_all is not None:
            close_all()

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

        if (
            not self.settings.channel_updates
            and is_channel_notification(notification)
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
