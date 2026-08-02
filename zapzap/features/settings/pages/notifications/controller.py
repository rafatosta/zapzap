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
        self._sync_notification_controls()

    def _load_settings(self):
        self.notify_groupBox.checkbox.setChecked(self.model.enabled)
        self.show_photo.checkbox.setChecked(self.model.show_photo)
        self.show_name.checkbox.setChecked(self.model.show_name)
        self.show_msg.checkbox.setChecked(self.model.show_message_preview)
        self.sound.checkbox.setChecked(self.model.sound)
        self.channel_updates.checkbox.setChecked(self.model.channel_updates)
        self.donationMessage.checkbox.setChecked(
            self.model.donation_message_enabled
        )

    def _sync_notification_controls(self):
        enabled = self.notify_groupBox.checkbox.isChecked()
        for row in self.notification_content_rows + self.notification_source_rows:
            row.setEnabled(enabled)
        self.sources_header.setEnabled(enabled)
        self.privacy_presets_button.setEnabled(enabled)

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
        self.sound.checkbox.toggled.connect(
            self._handle_toggle_sound
        )
        self.channel_updates.checkbox.toggled.connect(
            self._handle_toggle_channel_updates
        )
        self.donationMessage.checkbox.toggled.connect(
            self._handle_toggle_donation_message
        )
        self.show_all_action.triggered.connect(
            lambda: self._apply_privacy_preset(True, True, True)
        )
        self.hide_content_action.triggered.connect(
            lambda: self._apply_privacy_preset(True, True, False)
        )
        self.maximum_privacy_action.triggered.connect(
            lambda: self._apply_privacy_preset(False, False, False)
        )

    def _apply_privacy_preset(
        self,
        show_photo: bool,
        show_name: bool,
        show_message: bool,
    ):
        """Apply a shortcut through the existing switches and persistence."""
        self.show_photo.checkbox.setChecked(show_photo)
        self.show_name.checkbox.setChecked(show_name)
        self.show_msg.checkbox.setChecked(show_message)

    def _handle_toggle_notifications(self, is_enabled: bool):
        self.model.enabled = is_enabled
        self._sync_notification_controls()

    def _handle_toggle_show_photo(self, is_enabled: bool):
        self.model.show_photo = is_enabled

    def _handle_toggle_show_name(self, is_enabled: bool):
        self.model.show_name = is_enabled

    def _handle_toggle_show_message_preview(self, is_enabled: bool):
        self.model.show_message_preview = is_enabled

    def _handle_toggle_sound(self, is_enabled: bool):
        self.model.sound = is_enabled

    def _handle_toggle_channel_updates(self, is_enabled: bool):
        self.model.channel_updates = is_enabled

    def _handle_toggle_donation_message(self, is_enabled: bool):
        self.model.donation_message_enabled = is_enabled
