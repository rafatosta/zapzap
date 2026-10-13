"""Public macOS communication notifications with a Qt image fallback."""
from __future__ import annotations

import hashlib
import logging
from types import SimpleNamespace
from typing import TYPE_CHECKING
import uuid

from PyQt6.QtCore import QObject, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtWebEngineCore import QWebEngineNotification

from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.notifications.macos_native_notifications import NativeMacNotifications

if TYPE_CHECKING:
    from zapzap.features.browser.web.web_view import WebView


logger = logging.getLogger(__name__)


class MacosNotificationBackend(QObject):
    """Keep each native request paired with its own web notification/account."""

    def __init__(self):
        super().__init__()
        self._active = {}
        self._conversation_seed = uuid.uuid4().hex
        self._warned_communication_fallback = False
        try:
            self._native = NativeMacNotifications(self)
            self._native.event.connect(self._on_native_event)
        except (OSError, AttributeError):
            self._native = None
            logger.warning("Native macOS notifications unavailable; using Qt notifications")

    def available(self) -> bool:
        return True

    @staticmethod
    def _message_icon(notification: QWebEngineNotification) -> QIcon:
        if SettingsManager.get("notification/show_name", True):
            image = notification.icon()
            if not image.isNull():
                return QIcon(QPixmap.fromImage(image))
        application = QApplication.instance()
        return application.windowIcon() if application is not None else QIcon()

    def notify(
        self,
        page: WebView,
        notification: QWebEngineNotification,
        title: str,
        message: str,
        *,
        group_icon=None,
        group_name=None,
        sender_name=None,
    ):
        """Group inputs require independently supplied metadata, never text parsing.

        The normal WebEngine presenter supplies only one image. Optional group
        arguments are an explicit adapter seam; this backend does not discover
        contacts, groups, photos or message identities.
        """
        if self._native is None:
            self._notify_legacy(page, notification, title, message)
            return

        sender_visible = SettingsManager.get("notification/show_name", True)
        image = notification.icon() if sender_visible else None
        has_avatar = image is not None and not image.isNull()
        if not has_avatar:
            image = self._message_icon(notification).pixmap(128, 128).toImage()

        identifier = "zapzap-" + uuid.uuid4().hex
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._expire(identifier))
        closed = lambda: self._release(identifier, close_web=False)
        notification.closed.connect(closed)
        self._active[identifier] = SimpleNamespace(
            page=page, notification=notification, title=title, message=message,
            timer=timer, closed=closed, shown=False,
        )
        # Native completion is asynchronous. A lost response must not retain a
        # web object indefinitely; acceptance replaces this with display expiry.
        timer.start(5000)
        try:
            tag = notification.tag()
            # App-local, process-scoped identifiers; no raw account/chat key is
            # passed to Intents and no unbounded conversation map is retained.
            conversation_id = None
            if isinstance(tag, str) and tag:
                key = "\0".join((self._conversation_seed, str(page.user.id), tag))
                conversation_id = hashlib.sha256(key.encode("utf-8")).hexdigest()
            submitted = self._native.send(
                identifier, title, message, image,
                decorate=has_avatar and sender_visible,
                conversation_id=conversation_id,
                sender_name=sender_name if sender_visible and has_avatar else None,
                group_name=group_name if sender_visible and has_avatar else None,
                group_image=group_icon if sender_visible and has_avatar and group_name else None,
            )
        except (OSError, ValueError):
            submitted = False
        if not submitted:
            self._release(identifier, close_web=False)
            logger.warning("Native macOS submission failed; using Qt notifications")
            self._notify_legacy(page, notification, title, message)

    @pyqtSlot(str, int, int, int, int)
    def _on_native_event(self, identifier, event, error, attachments, authorization):
        entry = self._active.get(identifier)
        if entry is None:
            return
        if event == 7 and not self._warned_communication_fallback:
            self._warned_communication_fallback = True
            logger.warning(
                "macOS communication styling unavailable (code %s); using an image attachment",
                error,
            )
        if event == 1 and not entry.shown:
            try:
                entry.notification.show()
            except RuntimeError:
                self._release(identifier, close_web=False)
                return
            if self._active.get(identifier) is entry:
                entry.shown = True
                entry.timer.start(4000)
        elif event == 2:
            try:
                self._activate(entry.page, entry.notification)
            except Exception:
                logger.warning("Unable to activate macOS notification; withdrawing it")
            finally:
                self._release(identifier, close_web=True)
        elif event == 3:
            self._release(identifier, close_web=True)
        elif event == 4:
            self._release(identifier, close_web=False)
            logger.warning("Native macOS delivery failed (code %s); using Qt notifications", error)
            self._notify_legacy_async(entry.page, entry.notification, entry.title, entry.message)

    def _expire(self, identifier):
        entry = self._active.get(identifier)
        if entry is None:
            return
        pending = not entry.shown
        self._release(identifier, close_web=entry.shown)
        if pending:
            logger.warning("Native macOS submission timed out; using Qt notifications")
            self._notify_legacy_async(entry.page, entry.notification, entry.title, entry.message)

    def _notify_legacy_async(self, page, notification, title, message):
        # Native callbacks and timers run outside NotificationService.notify's
        # exception shield. A destroyed image/web/tray object must not escape
        # into the Qt event loop or include notification content in a log.
        try:
            self._notify_legacy(page, notification, title, message)
        except Exception:
            logger.warning("Qt macOS fallback delivery failed; dropping notification")

    def _release(self, identifier, close_web):
        entry = self._active.pop(identifier, None)
        if entry is None:
            return
        entry.timer.stop()
        entry.timer.deleteLater()
        try:
            entry.notification.closed.disconnect(entry.closed)
        except (TypeError, RuntimeError):
            pass
        self._native.remove(identifier)
        if close_web:
            try:
                entry.notification.close()
            except RuntimeError:
                pass

    def close_all(self):
        for identifier in list(self._active):
            self._release(identifier, close_web=True)

    @staticmethod
    def _activate(page, notification):
        application = QApplication.instance()
        main = application.getWindow() if application is not None else None
        if not main:
            return
        main.show()
        main.raise_()
        main.activateWindow()
        main.browser.activate_account(page.user.id)
        notification.click()

    def _notify_legacy(self, page, notification, title, message):
        from zapzap.features.tray.sys_tray_manager import SysTrayManager
        tray: QSystemTrayIcon = SysTrayManager.instance()._tray

        def _on_message_clicked():
            self._activate(page, notification)

        try:
            tray.messageClicked.disconnect()
        except TypeError:
            pass

        tray.messageClicked.connect(_on_message_clicked)
        tray.showMessage(title, message, self._message_icon(notification), 4000)
        notification.show()
