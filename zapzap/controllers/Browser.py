from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QAction
from zapzap.controllers.PageButton import PageButton
from zapzap.controllers.WebView import WebView
from zapzap.models.User import User
from zapzap.resources.SystemIcon import SystemIcon
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.AlertManager import AlertManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.views.ui_browser import Ui_Browser

from gettext import gettext as _


class Browser(QWidget, Ui_Browser):
    """Gerencia as páginas e interações do navegador no aplicativo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.parent = parent

        self.page_count = 0  # Contador de páginas
        self.page_buttons = {}  # Mapeamento entre botões e páginas

        self._initialize()

    def __del__(self):
        """Garante que todas as páginas sejam fechadas ao destruir o widget."""
        self.close_pages()

    # === Inicialização ===
    def _initialize(self):
        """Configura o navegador ao inicializar."""
        self._configure_signals()
        self._load_users()
        self._select_default_page()
        self._update_user_menu()
        self.settings_sidebar()

    def _configure_signals(self):
        """Configura os sinais do widget."""
        self.btn_new_account.clicked.connect(lambda: self.add_new_user())
        self.btn_new_chat_number.clicked.connect(
            lambda: self.parent.new_chat_by_phone())
        self.btn_new_chat.clicked.connect(lambda: self.parent.new_chat())
        self.btn_open_settings.clicked.connect(
            lambda: self.parent.open_settings())

    def _load_users(self):
        """Carrega os usuários e cria páginas correspondentes."""

        self._create_user_in_first_access()

        self.user_list = User.select()
        for user in self.user_list:
            self._add_page(user)

    def _create_user_in_first_access(self):
        """Cria o usuário no primeiro acesso."""
        # Não há usuários criados
        if User.count_users() == 0:
            User.create_new_user(icon=UserIcon.ICON_DEFAULT)

    def _select_default_page(self):
        """Seleciona a primeira página habilitada como padrão."""
        button, page = self._find_button_and_page_enabled()
        if button and page:
            self.switch_to_page(page, button)

    def add_new_user(self, new_user=None):
        """Adiciona um novo usuário e cria a página correspondente."""

        if not new_user:
            new_user = User.create_new_user()

        if new_user:
            self._add_page(new_user)
            self._update_user_menu()
        else:
            AlertManager.limit_users(self)

    # === Gerenciamento de Páginas ===

    def _add_page(self, user: User):
        """Adiciona uma nova página e o botão correspondente."""
        self.page_count += 1
        page_index = self.page_count

        # Criar uma nova página
        new_page = WebView(user, page_index)
        new_page.update_button_signal.connect(
            self.update_page_button_number_notifications
        )
        self.pages.addWidget(new_page)

        # Criar o botão correspondente
        page_button = PageButton(user, page_index)
        page_button.clicked.connect(
            lambda: self.switch_to_page(new_page, page_button))
        page_button.setObjectName(f"page_button_{page_index}")

        # Adicionar o botão ao layout e ao dicionário
        self.page_buttons_layout.addWidget(page_button)
        self.page_buttons[page_index] = page_button

    def disable_page(self, user: User):
        """Habilita ou desabilita uma página com base no status do usuário."""
        button, page = self._find_button_and_page_by_user(user)

        if button and page:
            if user.enable:
                button.show()
                page.enable_page()
            else:
                button.hide()
                page.disable_page()
        self._select_default_page()
        self._update_user_menu()

    def delete_page(self, user: User):
        """Remove uma página e seu botão correspondente."""
        button, page = self._find_button_and_page_by_user(user)

        if button and page:
            button.close()
            del self.page_buttons[button.page_index]
            page.remove_files()
        self._select_default_page()
        self._update_user_menu()

    def update_icons_page_button(self, user: User):
        """Atualiza os ícones de um botão específico com base no usuário."""
        button, page = self._find_button_and_page_by_user(user)

        if button and page:
            button.user = user
            page.user = user

        self._update_user_menu()

    def _update_user_menu(self):
        """Constroi o menu de usuários na barra de menu da janela principal."""
        # Reinicia o menu de usuários
        self.parent.menuUsers.clear()

        # Adiciona a opção para criar um novo usuário
        new_action = QAction(_("New account"), self)
        new_action.triggered.connect(lambda: self.add_new_user())
        new_action.setShortcut("Ctrl+U")
        self.parent.menuUsers.addAction(new_action)
        self.parent.menuUsers.addSeparator()

        # Adiciona ações para cada botão habilitado
        for count, button in enumerate(self.page_buttons.values(), start=1):
            if button.user.enable:
                # Define os itens da barra de menu Usuários
                new_action = QAction(
                    button.user.name if button.user.name != "" else _("Account {}").format(count), self)
                new_action.setShortcut(f'Ctrl+{count}')
                new_action.triggered.connect(button.clicked)
                self.parent.menuUsers.addAction(new_action)

    # === Funções Auxiliares ===
    def _find_button_and_page_by_user(self, user: User):
        """Busca o botão e a página correspondentes ao usuário."""
        for button in self.page_buttons.values():
            if button.user.id == user.id:
                page = self.pages.widget(button.page_index - 1)
                return button, page
        return None, None

    def _find_button_and_page_enabled(self):
        """Busca o primeiro botão e página habilitados."""
        for button in self.page_buttons.values():
            if button.user.enable:
                page = self.pages.widget(button.page_index - 1)
                return button, page
        return None, None

    # === Ações do Navegador ===
    def switch_to_page(self, page: WebView, button: PageButton):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        self._reset_button_styles()
        self.pages.setCurrentWidget(page)
        page.page().show_toast(page.user.name if page.user.name !=
                               "" else _("Account {}").format(page.page_index))
        button.selected()

    def close_pages(self):
        """Fecha e limpa todas as páginas existentes."""
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            if page:
                page.__del__()

    def reload_pages(self):
        """Recarrega todas as páginas existentes."""
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.load_page()

    def close_conversations(self):
        """Fecha todas as conversas abertas."""
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.close_conversation()

    def update_spellcheck(self):
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.configure_spellcheck()

    # === Notificações ===
    def update_page_button_number_notifications(self, page_index, number_notifications):
        """Atualiza o número de notificações de um botão específico."""
        if page_index in self.page_buttons:
            self.page_buttons[page_index].update_notifications(
                number_notifications)
            self._update_total_notifications()

    def _update_total_notifications(self):
        """Atualiza o total de notificações no SysTrayManager."""
        total_notifications = sum(
            button.number_notifications for button in self.page_buttons.values()
        )
        SysTrayManager.set_number_notifications(total_notifications)

    # === Estilo e Interface ===
    def _reset_button_styles(self):
        """Reseta os estilos de todos os botões."""
        for button in self.page_buttons.values():
            button.unselected()

    def set_theme_light(self):
        """Define o tema claro para as páginas e botões."""
        # Define o tema claro para as páginas
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.set_theme_light()

        # Define o tema claro para os botões
        self.__set_button_icons(SystemIcon.Type.Light)

    def set_theme_dark(self):
        """Define o tema escuro para as páginas e botões."""
        # Define o tema escuro para as páginas
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.set_theme_dark()

        # Define o tema escuro para os botões
        self.__set_button_icons(SystemIcon.Type.Dark)

    def __set_button_icons(self, theme):
        """Define os ícones dos botões com base no tema."""
        self.btn_new_account.setIcon(SystemIcon.get_icon("new_account", theme))
        self.btn_open_settings.setIcon(
            SystemIcon.get_icon("open_settings", theme))
        self.btn_new_chat.setIcon(SystemIcon.get_icon("new_chat", theme))
        self.btn_new_chat_number.setIcon(
            SystemIcon.get_icon("new_chat_number", theme))

    def settings_sidebar(self):
        """Mostra ou esconde a barra lateral"""
        if SettingsManager.get("system/sidebar", True):
            self.browser_sidebar.show()
        else:
            self.browser_sidebar.hide()
