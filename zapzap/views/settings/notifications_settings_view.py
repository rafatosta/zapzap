from gettext import gettext as _
from zapzap.views.components import Card, Section
from zapzap.views.settings_components import SettingsSwitchRow
from zapzap.views.settings_components import SettingsPage


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
        section = Section(
            _("Desktop notifications"),
            _("Choose whether ZapZap may show desktop notifications."),
        )
        card = Card()
        self.notify_groupBox = SettingsSwitchRow(
            _("Enable notifications"),
            _("Allow ZapZap to publish native desktop notifications for WhatsApp activity."),
        )
        card.add_widget(self.notify_groupBox)
        section.add_card(card)
        self.add_section(section)

    def _add_privacy_section(self):
        section = Section(
            _("Notification privacy"),
            _("Limit what is visible in notification banners."),
        )
        card = Card()
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
        card.add_widget(self.show_photo)
        card.add_widget(self.show_name)
        card.add_widget(self.show_msg)
        section.add_card(card)
        self.add_section(section)

    def _add_messages_section(self):
        section = Section(
            _("ZapZap messages"),
            _("Optional messages shown by ZapZap itself."),
        )
        card = Card()
        self.donationMessage = SettingsSwitchRow(
            _("Donation reminder"),
            _("Show occasional support messages from ZapZap."),
        )
        card.add_widget(self.donationMessage)
        section.add_card(card)
        self.add_section(section)
