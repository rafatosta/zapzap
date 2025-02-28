from PyQt6.QtWidgets import QWidget
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_notifications import Ui_PageNotifications


class PageNotifications(QWidget, Ui_PageNotifications):
    """Classe responsável por gerenciar a página de notificações nas configurações."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._initialize()

    def _initialize(self):
        """Inicializa a página carregando as configurações e configurando os sinais."""
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        """Carrega as configurações iniciais e aplica aos widgets."""
        # Configurações gerais
        self.notify_groupBox.setChecked(
            SettingsManager.get("notification/app", True)
        )
        self.show_photo.setChecked(
            SettingsManager.get("notification/show_photo", True)
        )
        self.show_name.setChecked(
            SettingsManager.get("notification/show_name", True)
        )
        self.show_msg.setChecked(
            SettingsManager.get("notification/show_msg", True)
        )
        self.donationMessage.setChecked(
            SettingsManager.get("notification/donation_message", False) # Desativado por padrão
        )

    def _connect_signals(self):
        """Conecta os sinais dos widgets aos métodos manipuladores."""
        self.notify_groupBox.toggled.connect(self._handle_toggle_notifications)
        self.show_photo.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_photo", self.show_photo.isChecked())
        )
        self.show_name.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_name", self.show_name.isChecked())
        )
        self.show_msg.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_msg", self.show_msg.isChecked())
        )
        self.donationMessage.clicked.connect(
            lambda: SettingsManager.set(
                "notification/donation_message", self.donationMessage.isChecked())
        )

    def _handle_toggle_notifications(self, is_enabled):
        """Manipula a ativação ou desativação geral das notificações."""
        SettingsManager.set("notification/app", is_enabled)
