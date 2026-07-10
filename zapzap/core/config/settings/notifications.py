"""Notification settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class NotificationSettings(BaseSettings):
    """Semantic access to notification settings."""

    _ENABLED = ("notification/app", True)
    _SHOW_PHOTO = ("notification/show_photo", True)
    _SHOW_NAME = ("notification/show_name", True)
    _SHOW_MESSAGE_PREVIEW = ("notification/show_msg", True)
    _DONATION_MESSAGE = ("notification/donation_message", False)

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
    def donation_message_enabled(self) -> bool:
        return self._get_bool(self._DONATION_MESSAGE)

    @donation_message_enabled.setter
    def donation_message_enabled(self, value: bool) -> None:
        self._set_bool(self._DONATION_MESSAGE, value)
