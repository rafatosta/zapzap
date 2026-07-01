from PyQt6.QtWidgets import QVBoxLayout, QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.pages.settings.notifications_settings_view import NotificationsSettingsView


class NotificationSettingsController(QWidget):
    """Controller for notification settings persistence and signals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._initialize()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = NotificationsSettingsView(self)
        layout.addWidget(self.view)

    def _initialize(self):
        """Load saved settings and connect view signals."""
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        self.view.notify_groupBox.checkbox.setChecked(
            SettingsManager.get("notification/app", True)
        )
        self.view.show_photo.checkbox.setChecked(
            SettingsManager.get("notification/show_photo", True)
        )
        self.view.show_name.checkbox.setChecked(
            SettingsManager.get("notification/show_name", True)
        )
        self.view.show_msg.checkbox.setChecked(
            SettingsManager.get("notification/show_msg", True)
        )
        self.view.donationMessage.checkbox.setChecked(
            SettingsManager.get("notification/donation_message", False)
        )

    def _connect_signals(self):
        self.view.notify_groupBox.checkbox.toggled.connect(
            self._handle_toggle_notifications
        )
        self.view.show_photo.checkbox.toggled.connect(
            lambda checked: SettingsManager.set("notification/show_photo", checked)
        )
        self.view.show_name.checkbox.toggled.connect(
            lambda checked: SettingsManager.set("notification/show_name", checked)
        )
        self.view.show_msg.checkbox.toggled.connect(
            lambda checked: SettingsManager.set("notification/show_msg", checked)
        )
        self.view.donationMessage.checkbox.toggled.connect(
            lambda checked: SettingsManager.set("notification/donation_message", checked)
        )

    def _handle_toggle_notifications(self, is_enabled):
        SettingsManager.set("notification/app", is_enabled)
