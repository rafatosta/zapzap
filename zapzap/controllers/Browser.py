from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from zapzap.controllers.PageButton import PageButton
from zapzap.controllers.WebView import WebView
from zapzap.models.User import User
from zapzap.services.SysTrayManager import SysTrayManager


class Browser(QWidget):
    """Gerencia as páginas e interações do navegador no aplicativo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_browser.ui", self)

        self.page_count = 0  # Contador de páginas
        self.page_buttons = {}  # Mapeamento entre botões e páginas

        self._load_users()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e fecha todas as páginas."""
        print("Widget Browser destruído")
        self.close_pages()

    # === Configuração Inicial ===
    def _load_users(self):
        """Carrega os usuários e cria páginas correspondentes."""
        self.user_list = User.select()
        for user in self.user_list:
            self.add_page(user)

    def _select_default_page(self):
        """Seleciona a página padrão, se houver páginas carregadas."""
        if self.page_buttons:
            self.page_buttons[1].selected()

    # === Gerenciamento de Páginas ===
    def add_page(self, user: User):
        """Adiciona uma nova página e cria o botão correspondente."""
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
            lambda: self.switch_to_page(new_page, page_button)
        )
        page_button.setObjectName(f"page_button_{page_index}")

        # Adicionar botão ao layout e registrar no dicionário
        self.page_buttons_layout.addWidget(page_button)
        self.page_buttons[page_index] = page_button

    def disable_page(self, user: User):
        print('disable page:', user.enable, user)

        # Obtém o botão e a página
        for button in self.page_buttons.values():
            if button.user.id == user.id:
                if user.enable:
                    print('Habilitar usuário')
                    button.show()
                    self.pages.widget(button.page_index-1).enable_page()
                else:
                    print("Desabilitar usuário")
                    # Esconde o Botão
                    button.hide()
                    # Esconde e pausa a página
                    self.pages.widget(button.page_index-1).disable_page()

    def delete_page(self, user: User):
        print('delete page:', user)
        for button in self.page_buttons.values():
            if button.user.id == user.id:
                button.close()
                self.pages.widget(button.page_index-1).remove_files()
                break

    def switch_to_page(self, page: WebView, button: PageButton):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        self._reset_button_styles()
        self.pages.setCurrentWidget(page)
        page.page().show_toast(f"Usuário {page.page_index} selecionado")
        button.selected()

    def close_pages(self):
        """Fecha e limpa todas as páginas existentes."""
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            if page:
                page.__del__()

    # === Ações do browser ===

    def reload_pages(self):
        """ Recarrega todas as páginas existentes."""
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.load_page()

    def close_conversations(self):
        """ Fechar todas as conversas abertas ao esconder a janela. """
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.whatsapp_page.close_conversation()

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

    def update_icons_page_button(self, user: User):
        print('update icons...')
        for button in self.page_buttons.values():
            if button.user.id == user.id:
                button.user = user
                self.pages.widget(button.page_index-1).user = user
                break

    # === Estilos e Interface ===
    def _reset_button_styles(self):
        """Reseta o estilo de todos os botões."""
        for button in self.page_buttons.values():
            button.unselected()

    def set_theme_light(self):
        """ Define o tema das páginas. """
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.whatsapp_page.set_theme_light()

    def set_theme_dark(self):
        """ Define o tema das páginas. """
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.whatsapp_page.set_theme_dark()
