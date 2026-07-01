from gettext import gettext as _

from PyQt6.QtWidgets import QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.settings_components import SettingsCard, SettingsPage, SettingsSection, SettingsSwitchRow


class PageNotifications(QWidget):
    """Classe responsável por gerenciar a página de notificações nas configurações."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._initialize()

    def _setup_ui(self):
        self.page = SettingsPage(
            _("Notifications"),
            _("Control desktop notifications, notification privacy, and ZapZap messages."),
            self,
        )
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.page)

        desktop = SettingsSection(_("Desktop notifications"), _("Choose whether ZapZap may show desktop notifications."))
        desktop_card = SettingsCard()
        self.notify_groupBox = SettingsSwitchRow(
            _("Enable notifications"),
            _("Allow ZapZap to publish native desktop notifications for WhatsApp activity."),
        )
        desktop_card.add_row(self.notify_groupBox)
        desktop.add_card(desktop_card)
        self.page.add_section(desktop)

        privacy = SettingsSection(_("Notification privacy"), _("Limit what is visible in notification banners."))
        privacy_card = SettingsCard()
        self.show_photo = SettingsSwitchRow(_("Show contact photo"), _("Display the sender avatar when it is available."))
        self.show_name = SettingsSwitchRow(_("Show contact name"), _("Display the sender or group name."))
        self.show_msg = SettingsSwitchRow(_("Show message preview"), _("Display the message text in the notification."))
        privacy_card.add_row(self.show_photo)
        privacy_card.add_row(self.show_name)
        privacy_card.add_row(self.show_msg)
        privacy.add_card(privacy_card)
        self.page.add_section(privacy)

        messages = SettingsSection(_("ZapZap messages"), _("Optional messages shown by ZapZap itself."))
        messages_card = SettingsCard()
        self.donationMessage = SettingsSwitchRow(
            _("Donation reminder"),
            _("Show occasional support messages from ZapZap."),
        )
        messages_card.add_row(self.donationMessage)
        messages.add_card(messages_card)
        self.page.add_section(messages)
        self.page.add_stretch()

    def _initialize(self):
        """Inicializa a página carregando as configurações e configurando os sinais."""
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        """Carrega as configurações iniciais e aplica aos widgets."""
        self.notify_groupBox.checkbox.setChecked(SettingsManager.get("notification/app", True))
        self.show_photo.checkbox.setChecked(SettingsManager.get("notification/show_photo", True))
        self.show_name.checkbox.setChecked(SettingsManager.get("notification/show_name", True))
        self.show_msg.checkbox.setChecked(SettingsManager.get("notification/show_msg", True))
        self.donationMessage.checkbox.setChecked(SettingsManager.get("notification/donation_message", False))

    def _connect_signals(self):
        """Conecta os sinais dos widgets aos métodos manipuladores."""
        self.notify_groupBox.checkbox.toggled.connect(self._handle_toggle_notifications)
        self.show_photo.checkbox.clicked.connect(
            lambda: SettingsManager.set("notification/show_photo", self.show_photo.checkbox.isChecked())
        )
        self.show_name.checkbox.clicked.connect(
            lambda: SettingsManager.set("notification/show_name", self.show_name.checkbox.isChecked())
        )
        self.show_msg.checkbox.clicked.connect(
            lambda: SettingsManager.set("notification/show_msg", self.show_msg.checkbox.isChecked())
        )
        self.donationMessage.checkbox.clicked.connect(
            lambda: SettingsManager.set("notification/donation_message", self.donationMessage.checkbox.isChecked())
        )

    def _handle_toggle_notifications(self, is_enabled):
        """Manipula a ativação ou desativação geral das notificações."""
        SettingsManager.set("notification/app", is_enabled)
