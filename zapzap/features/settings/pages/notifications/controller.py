from PyQt6.QtWidgets import QVBoxLayout

from zapzap.features.settings.pages.notifications.model import NotificationsSettingsModel
from zapzap.features.settings.pages.notifications.view import NotificationsSettingsView


class NotificationsSettingsController(NotificationsSettingsView):
    """Controller for notification settings persistence and signals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = NotificationsSettingsModel()
        self._initialize()

    def _initialize(self):
        """Load saved settings and connect view signals."""
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        self.notify_groupBox.checkbox.setChecked(self.model.enabled)
        self.show_photo.checkbox.setChecked(self.model.show_photo)
        self.show_name.checkbox.setChecked(self.model.show_name)
        self.show_msg.checkbox.setChecked(self.model.show_message_preview)
        self.donationMessage.checkbox.setChecked(
            self.model.donation_message_enabled
        )

    def _connect_signals(self):
        self.notify_groupBox.checkbox.toggled.connect(
            self._handle_toggle_notifications
        )
        self.show_photo.checkbox.toggled.connect(
            self._handle_toggle_show_photo
        )
        self.show_name.checkbox.toggled.connect(
            self._handle_toggle_show_name
        )
        self.show_msg.checkbox.toggled.connect(
            self._handle_toggle_show_message_preview
        )
        self.donationMessage.checkbox.toggled.connect(
            self._handle_toggle_donation_message
        )

    def _handle_toggle_notifications(self, is_enabled: bool):
        self.model.enabled = is_enabled

    def _handle_toggle_show_photo(self, is_enabled: bool):
        self.model.show_photo = is_enabled

    def _handle_toggle_show_name(self, is_enabled: bool):
        self.model.show_name = is_enabled

    def _handle_toggle_show_message_preview(self, is_enabled: bool):
        self.model.show_message_preview = is_enabled

    def _handle_toggle_donation_message(self, is_enabled: bool):
        self.model.donation_message_enabled = is_enabled