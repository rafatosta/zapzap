from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QMenu, QVBoxLayout, QWidget

from zapzap.features.settings.components import (
    SettingsCard,
    SettingsPage,
    SettingsSwitchRow,
)
from zapzap.ui.components import Button, Label


class NotificationsSettingsView(SettingsPage):
    """Composable view for notification settings, without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Notifications"),
            _("Configure notifications, privacy, and ZapZap messages."),
            parent,
        )
        self.setObjectName("NotificationsSettingsView")
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._add_notifications_section()
        self._add_messages_section()

    def _add_notifications_section(self):
        section = self._create_section(
            _("Notifications"),
            _("Choose which information may appear in notifications."),
            with_privacy_menu=True,
        )
        card = SettingsCard()
        self.notify_groupBox = SettingsSwitchRow(
            _("Desktop notifications"),
            _(
                "Show WhatsApp notifications using the desktop notification "
                "system."
            ),
        )
        self._configure_accessibility(self.notify_groupBox)
        self.show_photo = SettingsSwitchRow(
            _("Contact photo"),
            _("Show the sender's photo when available."),
        )
        self.show_name = SettingsSwitchRow(
            _("Contact name"),
            _("Show the sender or group name."),
        )
        self.show_msg = SettingsSwitchRow(
            _("Message preview"),
            _("Show the content of the received message."),
        )
        self.notification_content_rows = (
            self.show_photo,
            self.show_name,
            self.show_msg,
        )
        for row in self.notification_content_rows:
            self._configure_accessibility(row)
        card.add_group(
            self.notify_groupBox,
            self.notification_content_rows,
            child_dividers=True,
        )
        section.layout().addWidget(card)
        self.add_section(section)

    def _add_messages_section(self):
        section = self._create_section(
            _("ZapZap messages"),
            _("Control occasional messages shown by the application itself."),
        )
        card = SettingsCard()
        self.donationMessage = SettingsSwitchRow(
            _("Support reminders"),
            _(
                "Occasionally show messages supporting ZapZap's "
                "development."
            ),
        )
        self._configure_accessibility(self.donationMessage)
        card.add_row(self.donationMessage)
        section.layout().addWidget(card)
        self.add_section(section)

    def _create_section(self, title, description="", with_privacy_menu=False):
        """Create a compact section with an optional action in its header."""
        section = QWidget(self)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header = QWidget(section)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_label = Label(title, "section_title", header)
        title_label.setObjectName("SettingsSectionTitle")
        header_layout.addWidget(title_label, 1)

        if with_privacy_menu:
            self.privacy_presets_button = Button(_("Privacy"), parent=header)
            self.privacy_presets_button.setAccessibleName(
                _("Privacy presets")
            )
            self.privacy_presets_button.setAccessibleDescription(
                _("Quickly choose which notification details are visible.")
            )
            self.privacy_presets_menu = QMenu(self.privacy_presets_button)
            self.show_all_action = self.privacy_presets_menu.addAction(
                _("Show everything")
            )
            self.hide_content_action = self.privacy_presets_menu.addAction(
                _("Hide content")
            )
            self.maximum_privacy_action = self.privacy_presets_menu.addAction(
                _("Maximum privacy")
            )
            self.privacy_presets_button.setMenu(self.privacy_presets_menu)
            header_layout.addWidget(
                self.privacy_presets_button,
                0,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )

        layout.addWidget(header)
        if description:
            description_label = Label(
                description,
                "section_description",
                section,
            )
            description_label.setObjectName("SettingsSectionDescription")
            layout.addWidget(description_label)
        return section

    @staticmethod
    def _configure_accessibility(row):
        """Associate a switch with the row's visible title and description."""
        title = row.title_label.text()
        description = (
            row.description_label.text() if row.description_label else ""
        )
        row.checkbox.setAccessibleName(title)
        row.checkbox.setAccessibleDescription(description)
        row.title_label.setBuddy(row.checkbox)
