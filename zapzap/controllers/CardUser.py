from PyQt6.QtWidgets import QWidget, QApplication, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QActionGroup

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

        # Add User Agent selector
        from PyQt6.QtWidgets import QComboBox
        from zapzap.webengine.WebView import WebView
        self.ua_selector = QComboBox(self)
        self.ua_selector.setToolTip(_("Select User-Agent for this account"))
        self.ua_selector.addItems(list(WebView.USER_AGENTS.keys()))
        selected_ua = SettingsManager.get(f"{self.user.id}/user_agent", "Default")
        self.ua_selector.setCurrentText(selected_ua)
        self.gridLayout.addWidget(self.ua_selector, 2, 0, 1, 3)

    def _setup_signals(self):
        """Configura os sinais e suas respectivas ações."""
        self.silence.clicked.connect(self._handle_silence_action)
        self.disable.clicked.connect(self._handle_disable_action)
        self.delete.clicked.connect(self._handle_delete_action)
        self.name.editingFinished.connect(self._update_user_name)
        self.icon.clicked.connect(self._handle_icon_action)
        self.ua_selector.currentTextChanged.connect(self._handle_ua_change)

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
        self.set_user_enabled(self.user, not self.disable.isChecked())
        self._update_user_icon()

    def _handle_silence_action(self):
        """Ativa ou desativa notificações do usuário."""
        self.set_user_notifications(self.user, not self.silence.isChecked())
        self._update_user_icon()

    def _handle_delete_action(self):
        """Exclui o usuário."""
        self.delete_user(
            self,
            self.user,
            on_deleted=lambda: (self.close(), self.setParent(None)),
        )

    def _handle_icon_action(self):
        """Gera novo ícone aleatório para o usuário."""
        self.regenerate_user_icon(self.user)
        self._update_user_icon()

    def _update_user_name(self):
        """Atualiza o nome do usuário no banco de dados."""
        self.user.name = self.name.text()
        browser = self._get_browser()
        if browser:
            browser.update_icons_page_button(self.user)

    def _show_context_menu(self, position):
        """Exibe o menu de contexto do ícone."""
        menu = self.create_icon_context_menu(self, self.user)
        menu.exec(self.icon.mapToGlobal(position))

    def _restore_default(self):
        """Restaura o ícone padrão do usuário."""
        self.restore_default_icon(self.user)
        self._update_user_icon()

    def _handle_ua_change(self, text):
        self.set_user_agent(self, self.user, text)

    @staticmethod
    def _get_browser():
        app = QApplication.instance()
        if not app:
            return None
        window = app.getWindow()
        return getattr(window, "browser", None) if window else None

    @classmethod
    def set_user_enabled(cls, user: User, enabled: bool):
        user.enable = enabled
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)
            browser.disable_page(user)

    @classmethod
    def set_user_notifications(cls, user: User, enabled: bool):
        SettingsManager.set(f"{user.id}/notification", enabled)
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)

    @classmethod
    def delete_user(cls, parent, user: User, on_deleted=None):
        if AlertManager.question(parent, _("Confirm exclusion"), _("Are you sure you want to delete this item?")):
            browser = cls._get_browser()
            if browser:
                browser.delete_page(user)
            user.remove()
            if on_deleted:
                on_deleted()

    @classmethod
    def regenerate_user_icon(cls, user: User):
        user.icon = UserIcon.get_new_icon_svg()
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)

    @classmethod
    def restore_default_icon(cls, user: User):
        user.icon = UserIcon.ICON_DEFAULT
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)

    @staticmethod
    def set_user_agent(parent, user: User, text: str):
        SettingsManager.set(f"{user.id}/user_agent", text)
        AlertManager.information(parent, _("User-Agent Changed"), _("Please restart this session (or the application) to apply the new User-Agent."))

    @classmethod
    def create_icon_context_menu(cls, parent, user: User):
        menu = QMenu(parent)

        generate_icon_action = menu.addAction(_("Generate new colors for the icon"))
        generate_icon_action.triggered.connect(lambda: cls.regenerate_user_icon(user))

        restore_action = menu.addAction(_("Restore standard"))
        restore_action.triggered.connect(lambda: cls.restore_default_icon(user))

        return menu

    @classmethod
    def create_page_button_context_menu(cls, parent, user: User):
        from zapzap.webengine.WebView import WebView

        menu = QMenu(parent)

        silence_action = menu.addAction(_("Do not disturb"))
        silence_action.setCheckable(True)
        silence_action.setChecked(
            not SettingsManager.get(f"{user.id}/notification", True)
        )
        silence_action.toggled.connect(
            lambda checked: cls.set_user_notifications(user, not checked)
        )

        disable_action = menu.addAction(_("Disable"))
        disable_action.setCheckable(True)
        disable_action.setChecked(not user.enable)
        disable_action.toggled.connect(
            lambda checked: cls.set_user_enabled(user, not checked)
        )

        user_agent_menu = menu.addMenu(_("User-Agent"))
        user_agent_group = QActionGroup(user_agent_menu)
        user_agent_group.setExclusive(True)
        selected_ua = SettingsManager.get(f"{user.id}/user_agent", "Default")
        for user_agent_name in WebView.USER_AGENTS.keys():
            user_agent_action = user_agent_menu.addAction(user_agent_name)
            user_agent_action.setCheckable(True)
            user_agent_action.setChecked(user_agent_name == selected_ua)
            user_agent_action.triggered.connect(
                lambda checked, ua=user_agent_name: checked and cls.set_user_agent(parent, user, ua)
            )
            user_agent_group.addAction(user_agent_action)

        menu.addSeparator()

        generate_icon_action = menu.addAction(_("Generate new colors for the icon"))
        generate_icon_action.triggered.connect(lambda: cls.regenerate_user_icon(user))

        restore_action = menu.addAction(_("Restore standard"))
        restore_action.triggered.connect(lambda: cls.restore_default_icon(user))

        if user.id != User.USER_DEFAULT:
            menu.addSeparator()
            delete_action = menu.addAction(_("Delete"))
            delete_action.triggered.connect(lambda: cls.delete_user(parent, user))

        return menu
