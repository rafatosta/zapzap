"""Notification settings domain."""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from zapzap.core.config.settings.base import BaseSettings


class NotificationSettingsEvents(QObject):
    """Notify live components when a notification preference changes."""

    respect_dnd_changed = pyqtSignal()


notification_settings_events = NotificationSettingsEvents()


class NotificationSettings(BaseSettings):
    """Semantic access to notification settings."""

    _ENABLED = ("notification/app", True)
    _SHOW_PHOTO = ("notification/show_photo", True)
    _SHOW_NAME = ("notification/show_name", True)
    _SHOW_MESSAGE_PREVIEW = ("notification/show_msg", True)
    _SOUND = ("notification/sound", True)
    _RESPECT_DND = ("notification/respect_dnd", True)
    # This legacy key stores whether reminders are hidden, despite its name.
    _DONATION_MESSAGE_HIDDEN = ("notification/donation_message", False)

    @property
    def enabled(self) -> bool:
        return self._get_bool(self._ENABLED)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_bool(self._ENABLED, value)

    @property
    def show_photo(self) -> bool:
        return self._get_bool(self._SHOW_PHOTO)

    @show_photo.setter
    def show_photo(self, value: bool) -> None:
        self._set_bool(self._SHOW_PHOTO, value)

    @property
    def show_name(self) -> bool:
        return self._get_bool(self._SHOW_NAME)

    @show_name.setter
    def show_name(self, value: bool) -> None:
        self._set_bool(self._SHOW_NAME, value)

    @property
    def show_message_preview(self) -> bool:
        return self._get_bool(self._SHOW_MESSAGE_PREVIEW)

    @show_message_preview.setter
    def show_message_preview(self, value: bool) -> None:
        self._set_bool(self._SHOW_MESSAGE_PREVIEW, value)

    @property
    def sound(self) -> bool:
        return self._get_bool(self._SOUND)

    @sound.setter
    def sound(self, value: bool) -> None:
        self._set_bool(self._SOUND, value)

    @property
    def respect_dnd(self) -> bool:
        """Whether the message tone follows the desktop Do Not Disturb."""
        return self._get_bool(self._RESPECT_DND)

    @respect_dnd.setter
    def respect_dnd(self, value: bool) -> None:
        self._set_bool(self._RESPECT_DND, value)
        notification_settings_events.respect_dnd_changed.emit()

    @property
    def donation_message_enabled(self) -> bool:
        """Whether support reminders may be shown."""
        return not self._get_bool(self._DONATION_MESSAGE_HIDDEN)

    @donation_message_enabled.setter
    def donation_message_enabled(self, value: bool) -> None:
        self._set_bool(self._DONATION_MESSAGE_HIDDEN, not value)
