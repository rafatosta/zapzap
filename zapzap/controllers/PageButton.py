from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize

from zapzap.models import User
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.SettingsManager import SettingsManager


class PageButton(QPushButton):
    """Botão de página com ícones de usuário e gerenciamento de estilo."""

    number_notifications = 0
    isSelected = False

    # Estilos
    STYLE_NORMAL = """
    QPushButton {
       qproperty-iconSize: 25px;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding: 2px;
    }
    """

    STYLE_HOVER = """
    QPushButton {
      background-color: rgba(225, 225, 225, 0.3);
      border-radius: 2px;
      height: 30px;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding: 2px;
    }
    """

    STYLE_SELECTED = """
    QPushButton {
      background-color: rgba(225, 225, 225, 0.3);
      border-radius: 2px;
      height: 30px;
      border-left: 3px solid #00BD95;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding: 2px;
    }
    """

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)
        self._user = user
        self.page_index = page_index

        self._setup_ui()
        self.update_user_icon()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        self.update_user_icon()

    def _setup_ui(self):
        """Configura a interface do botão."""
        self.setFlat(True)
        self.setMinimumSize(QSize(40, 40))
        self.setMaximumSize(QSize(40, 40))
        self.setStyleSheet(self.STYLE_NORMAL)

    def update_user_icon(self):
        """Atualiza o ícone do usuário e a dica de ferramenta."""
        # Define o tipo de ícone com base no status do usuário
        user_icon_type = UserIcon.Type.Default
        if not self._user.enable:
            user_icon_type = UserIcon.Type.Disable
        elif not SettingsManager.get(f"{self._user.id}/notification", False):
            user_icon_type = UserIcon.Type.Silence

        # Atualiza o ícone e a dica de ferramenta
        self.setIcon(UserIcon.get_icon(self._user.icon, user_icon_type))
        tooltip = (
            f"{self._user.name} ({self.number_notifications})"
            if self.number_notifications > 0
            else self._user.name
        )
        self.setToolTip(tooltip)

    def update_notifications(self, number_notifications):
        """Atualiza o número de notificações do botão."""
        self.number_notifications = number_notifications
        self.update_user_icon()

    ## Eventos ##

    def selected(self):
        """Define o botão como selecionado."""
        self.isSelected = True
        self.setStyleSheet(self.STYLE_SELECTED)

    def unselected(self):
        """Define o botão como não selecionado."""
        self.isSelected = False
        self.setStyleSheet(self.STYLE_NORMAL)

    def enterEvent(self, event):
        """Evento ao entrar com o mouse sobre o botão."""
        self.setStyleSheet(
            self.STYLE_SELECTED if self.isSelected else self.STYLE_HOVER)

    def leaveEvent(self, event):
        """Evento ao sair com o mouse do botão."""
        self.setStyleSheet(
            self.STYLE_SELECTED if self.isSelected else self.STYLE_NORMAL)
