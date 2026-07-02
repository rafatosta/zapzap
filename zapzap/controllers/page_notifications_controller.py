"""Controller for the notifications settings page."""

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.pages import PageNotificationsView


class PageNotificationsController(PageNotificationsView):
    """Controls notification settings behavior for PageNotificationsView."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initialize()

    def _initialize(self):
        """Load current settings and connect view signals."""
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        """Load initial notification settings into the view widgets."""
        self.notify_groupBox.checkbox.setChecked(
            SettingsManager.get("notification/app", True)
        )
        self.show_photo.checkbox.setChecked(
            SettingsManager.get("notification/show_photo", True)
        )
        self.show_name.checkbox.setChecked(
            SettingsManager.get("notification/show_name", True)
        )
        self.show_msg.checkbox.setChecked(
            SettingsManager.get("notification/show_msg", True)
        )
        self.donationMessage.checkbox.setChecked(
            SettingsManager.get("notification/donation_message", False)
        )

    def _connect_signals(self):
        """Connect view widget signals to settings handlers."""
        self.notify_groupBox.checkbox.toggled.connect(
            self._handle_toggle_notifications
        )
        self.show_photo.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_photo",
                self.show_photo.checkbox.isChecked(),
            )
        )
        self.show_name.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_name",
                self.show_name.checkbox.isChecked(),
            )
        )
        self.show_msg.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_msg",
                self.show_msg.checkbox.isChecked(),
            )
        )
        self.donationMessage.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/donation_message",
                self.donationMessage.checkbox.isChecked(),
            )
        )

    def _handle_toggle_notifications(self, is_enabled):
        """Persist the global notifications enabled state."""
        SettingsManager.set("notification/app", is_enabled)
