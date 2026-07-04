from gettext import gettext as _

from zapzap.views.settings_components import (
    SettingsActionRow,
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsPathRow,
    SettingsSection,
    SettingsSelectRow,
    SettingsSwitchRow,
)



class NotificationsSettingsView(SettingsPage):
    """Composable view for notification settings, without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Notifications"),
            _("Control desktop notifications, notification privacy, and ZapZap messages."),
            parent,
        )
        self.setObjectName("NotificationsSettingsView")
        self._setup_ui()
        self._apply_style()
        self.add_stretch()

    def _setup_ui(self):
        self._add_desktop_section()
        self._add_privacy_section()
        self._add_messages_section()

    def _add_desktop_section(self):
        section = SettingsSection(
            _("Desktop notifications"),
            _("Choose whether ZapZap may show desktop notifications."),
        )
        card = SettingsCard()
        self.notify_groupBox = SettingsSwitchRow(
            _("Enable notifications"),
            _("Allow ZapZap to publish native desktop notifications for WhatsApp activity."),
        )
        card.add_row(self.notify_groupBox)
        section.add_card(card)
        self.add_section(section)

    def _add_privacy_section(self):
        section = SettingsSection(
            _("Notification privacy"),
            _("Limit what is visible in notification banners."),
        )
        card = SettingsCard()
        self.show_photo = SettingsSwitchRow(
            _("Show contact photo"),
            _("Display the sender avatar when it is available."),
        )
        self.show_name = SettingsSwitchRow(
            _("Show contact name"),
            _("Display the sender or group name."),
        )
        self.show_msg = SettingsSwitchRow(
            _("Show message preview"),
            _("Display the message text in the notification."),
        )
        card.add_row(self.show_photo)
        card.add_row(self.show_name)
        card.add_row(self.show_msg)
        section.add_card(card)
        self.add_section(section)

    def _add_messages_section(self):
        section = SettingsSection(
            _("ZapZap messages"),
            _("Optional messages shown by ZapZap itself."),
        )
        card = SettingsCard()
        self.donationMessage = SettingsSwitchRow(
            _("Donation reminder"),
            _("Show occasional support messages from ZapZap."),
        )
        card.add_row(self.donationMessage)
        section.add_card(card)
        self.add_section(section)
