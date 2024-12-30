from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from zapzap.models import User
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.SettingsManager import SettingsManager


class CardUser(QWidget):
    def __init__(self, user: User = None, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_card_user.ui", self)

        self.user = user

        self._setup_signals()
        self._load_data()
        self._update_user_icon()

    def _setup_signals(self):
        """Configura os sinais para os elementos da interface."""
        self.silence.clicked.connect(self._handle_silence_action)
        self.disable.clicked.connect(self._handle_disable_action)
        self.delete.clicked.connect(self._handle_delete_action)

    def _load_data(self):
        """Carrega os dados do usuário na interface."""
        if self.user:
            self.name.setText(self.user.name)
            self.disable.setChecked(not self.user.enable)
            self.silence.setChecked(
                not SettingsManager.get(f"{self.user.id}/notification", False)
            )

    def _handle_disable_action(self):
        """Ação para habilitar/desabilitar o usuário."""
        if self.user:
            self.user.enable = not self.disable.isChecked()
            self._update_user_icon()

    def _handle_silence_action(self):
        """Ação para ativar/desativar notificações do usuário."""
        if self.user:
            SettingsManager.set(
                f"{self.user.id}/notification", not self.silence.isChecked()
            )
            self._update_user_icon()

    def _handle_delete_action(self):
        """Ação para excluir o usuário."""
        print("Usuário excluído!")  # Aqui você pode adicionar a lógica de exclusão.

    def _update_user_icon(self):
        """Atualiza o ícone do usuário com base em seu status."""
        if not self.user:
            return

        user_icon_type = UserIcon.Type.Default
        if not self.user.enable:
            user_icon_type = UserIcon.Type.Disable
        elif not SettingsManager.get(f"{self.user.id}/notification", False):
            user_icon_type = UserIcon.Type.Silence

        self.icon.setIcon(UserIcon.get_icon(self.user.icon, user_icon_type))
