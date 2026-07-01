from PyQt6.QtWidgets import QVBoxLayout, QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.pages import PageNotificationsView


class PageNotifications(QWidget):
    """Classe responsável por gerenciar a página de notificações nas configurações."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._initialize()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = PageNotificationsView(self)
        layout.addWidget(self.view)

    def _initialize(self):
        """Inicializa a página carregando as configurações e configurando os sinais."""
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        """Carrega as configurações iniciais e aplica aos widgets."""
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
        """Conecta os sinais dos widgets aos métodos manipuladores."""
        self.view.notify_groupBox.checkbox.toggled.connect(
            self._handle_toggle_notifications
        )
        self.view.show_photo.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_photo",
                self.view.show_photo.checkbox.isChecked(),
            )
        )
        self.view.show_name.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_name",
                self.view.show_name.checkbox.isChecked(),
            )
        )
        self.view.show_msg.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/show_msg",
                self.view.show_msg.checkbox.isChecked(),
            )
        )
        self.view.donationMessage.checkbox.clicked.connect(
            lambda: SettingsManager.set(
                "notification/donation_message",
                self.view.donationMessage.checkbox.isChecked(),
            )
        )

    def _handle_toggle_notifications(self, is_enabled):
        """Manipula a ativação ou desativação geral das notificações."""
        SettingsManager.set("notification/app", is_enabled)
