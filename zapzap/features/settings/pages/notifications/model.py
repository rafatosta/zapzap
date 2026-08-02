from __future__ import annotations

from zapzap.core.config.settings.notifications import NotificationSettings


class NotificationsSettingsModel:
    """Model for notification settings persistence."""

    def __init__(self) -> None:
        self._settings = NotificationSettings()

    @property
    def enabled(self) -> bool:
        """Whether desktop notifications are enabled."""
        return self._settings.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._settings.enabled = value

    @property
    def sound(self) -> bool:
        """Whether the notification server may play its alert sound."""
        return self._settings.sound

    @sound.setter
    def sound(self, value: bool) -> None:
        self._settings.sound = value

    @property
    def channel_updates(self) -> bool:
        """Whether posts from followed WhatsApp Channels may notify."""
        return self._settings.channel_updates

    @channel_updates.setter
    def channel_updates(self, value: bool) -> None:
        self._settings.channel_updates = value

    @property
    def show_photo(self) -> bool:
        """Whether contact photos are shown in notifications."""
        return self._settings.show_photo

    @show_photo.setter
    def show_photo(self, value: bool) -> None:
        self._settings.show_photo = value

    @property
    def show_name(self) -> bool:
        """Whether contact names are shown in notifications."""
        return self._settings.show_name

    @show_name.setter
    def show_name(self, value: bool) -> None:
        self._settings.show_name = value

    @property
    def show_message_preview(self) -> bool:
        """Whether message text is shown in notifications."""
        return self._settings.show_message_preview

    @show_message_preview.setter
    def show_message_preview(self, value: bool) -> None:
        self._settings.show_message_preview = value

    @property
    def donation_message_enabled(self) -> bool:
        """Whether ZapZap donation/support reminders are enabled."""
        return self._settings.donation_message_enabled

    @donation_message_enabled.setter
    def donation_message_enabled(self, value: bool) -> None:
        self._settings.donation_message_enabled = value
