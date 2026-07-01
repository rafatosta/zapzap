from __future__ import annotations

from zapzap.services.SettingsManager import SettingsManager


class NotificationSettingsModel:
    """Model for notification settings persistence.

    This class hides SettingsManager keys from controllers and views.
    Controllers should access notification settings only through semantic
    properties such as `enabled`, `show_photo`, and `show_message_preview`.
    """

    _ENABLED = ("notification/app", True)
    _SHOW_PHOTO = ("notification/show_photo", True)
    _SHOW_NAME = ("notification/show_name", True)
    _SHOW_MESSAGE_PREVIEW = ("notification/show_msg", True)
    _DONATION_MESSAGE = ("notification/donation_message", False)

    def _get_bool(self, setting: tuple[str, bool]) -> bool:
        key, default = setting
        return bool(SettingsManager.get(key, default))

    def _set_bool(self, setting: tuple[str, bool], value: bool) -> None:
        key, _default = setting
        SettingsManager.set(key, bool(value))

    @property
    def enabled(self) -> bool:
        """Whether desktop notifications are enabled."""
        return self._get_bool(self._ENABLED)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_bool(self._ENABLED, value)

    @property
    def show_photo(self) -> bool:
        """Whether contact photos are shown in notifications."""
        return self._get_bool(self._SHOW_PHOTO)

    @show_photo.setter
    def show_photo(self, value: bool) -> None:
        self._set_bool(self._SHOW_PHOTO, value)

    @property
    def show_name(self) -> bool:
        """Whether contact names are shown in notifications."""
        return self._get_bool(self._SHOW_NAME)

    @show_name.setter
    def show_name(self, value: bool) -> None:
        self._set_bool(self._SHOW_NAME, value)

    @property
    def show_message_preview(self) -> bool:
        """Whether message text is shown in notifications."""
        return self._get_bool(self._SHOW_MESSAGE_PREVIEW)

    @show_message_preview.setter
    def show_message_preview(self, value: bool) -> None:
        self._set_bool(self._SHOW_MESSAGE_PREVIEW, value)

    @property
    def donation_message_enabled(self) -> bool:
        """Whether ZapZap donation/support reminders are enabled."""
        return self._get_bool(self._DONATION_MESSAGE)

    @donation_message_enabled.setter
    def donation_message_enabled(self, value: bool) -> None:
        self._set_bool(self._DONATION_MESSAGE, value)