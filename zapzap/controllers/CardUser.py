from PyQt6.QtWidgets import QWidget, QApplication, QMenu
from PyQt6.QtCore import Qt

from zapzap.models.User import User
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.AlertManager import AlertManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_card_user import Ui_CardUser

from gettext import gettext as _

class CardUser(QWidget, Ui_CardUser):
    def __init__(self, user: User = None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.user = user

        self._initialize()

    def _initialize(self):
        """Inicializa o card do usuário."""
        self._setup_ui()
        self._setup_signals()
        self._load_data()
        self._update_user_icon()

    def _setup_ui(self):
        """Configura a interface inicial do card de usuário."""
        if self.user.id == User.USER_DEFAULT:  # Oculta exclusão para o usuário padrão
            self.delete.hide()
            # Conectar evento de menu de contexto
            self.icon.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu)
            self.icon.customContextMenuRequested.connect(
                self._show_context_menu)

    def _setup_signals(self):
        """Configura os sinais e suas respectivas ações."""
        self.silence.clicked.connect(self._handle_silence_action)
        self.disable.clicked.connect(self._handle_disable_action)
        self.delete.clicked.connect(self._handle_delete_action)
        self.name.editingFinished.connect(self._update_user_name)
        self.icon.clicked.connect(self._handle_icon_action)

    def _load_data(self):
        """Carrega os dados do usuário na interface."""
        self.name.setText(self.user.name)
        self.disable.setChecked(not self.user.enable)
        self.silence.setChecked(
            not SettingsManager.get(f"{self.user.id}/notification", True)
        )

    def _update_user_icon(self):
        """Atualiza o ícone do usuário com base no seu status."""
        user_icon_type = UserIcon.Type.Default

        if not self.user.enable:
            user_icon_type = UserIcon.Type.Disable
        elif not SettingsManager.get(f"{self.user.id}/notification", True):
            user_icon_type = UserIcon.Type.Silence

        self.icon.setIcon(UserIcon.get_icon(self.user.icon, user_icon_type))

    def _handle_disable_action(self):
        """Habilita ou desabilita o usuário."""
        self.user.enable = not self.disable.isChecked()
        self._update_user_icon()

        browser = QApplication.instance().getWindow().browser
        browser.update_icons_page_button(self.user)
        browser.disable_page(self.user)

    def _handle_silence_action(self):
        """Ativa ou desativa notificações do usuário."""
        SettingsManager.set(
            f"{self.user.id}/notification", not self.silence.isChecked()
        )
        self._update_user_icon()

        QApplication.instance().getWindow().browser.update_icons_page_button(self.user)

    def _handle_delete_action(self):
        """Exclui o usuário."""

        if AlertManager.question(self, _("Confirm exclusion"), _("Are you sure you want to delete this item?")):
            QApplication.instance().getWindow().browser.delete_page(self.user)
            self.user.remove()
            self.close()
            self.setParent(None)
        else:
            print("Ação de exclusão cancelada.")

    def _handle_icon_action(self):
        """Gera novo ícone aleatório para o usuário."""
        self.user.icon = UserIcon.get_new_icon_svg()

        self._update_user_icon()

        QApplication.instance().getWindow().browser.update_icons_page_button(self.user)

    def _update_user_name(self):
        """Atualiza o nome do usuário no banco de dados."""
        self.user.name = self.name.text()
        QApplication.instance().getWindow().browser.update_icons_page_button(self.user)

    def _show_context_menu(self, position):
        # Criar menu
        menu = QMenu(self)

        # Adicionar ação "Restaurar padrão"
        restore_action = menu.addAction(_("Restore standard"))
        restore_action.triggered.connect(self._restore_default)

        # Exibir menu na posição do cursor
        menu.exec(self.icon.mapToGlobal(position))

    def _restore_default(self):
        # Ação executada ao clicar em "Restaurar padrão"
        self.user.icon = UserIcon.ICON_DEFAULT
        self._update_user_icon()

        QApplication.instance().getWindow().browser.update_icons_page_button(self.user)
