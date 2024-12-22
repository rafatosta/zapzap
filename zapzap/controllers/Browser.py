from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from zapzap.controllers.PageButton import PageButton
from zapzap.controllers.WebView import WebView
from zapzap.models.User import User
from zapzap.services.SysTray import SysTray


class Browser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_browser.ui", self)

        self.page_count = 0  # Contador de páginas
        self.page_buttons = {}  # Dicionário para mapear botões às páginas

        self.load_users()

        # Seleciona a conta padrão, se houver
        if self.page_buttons:
            self.page_buttons[1].selected()

    def load_users(self):
        """Carrega os usuários e cria páginas correspondentes."""
        self.user_list = User.select()
        for user in self.user_list:
            self.add_page(user)

    def add_page(self, user: User):
        """Adiciona uma nova página e cria o botão correspondente."""
        self.page_count += 1
        page_index = self.page_count

        # Criar uma nova página
        new_page = WebView(user, page_index)
        new_page.update_button_signal.connect(
            self.update_page_button_number_notifications)
        self.pages.addWidget(new_page)

        # Criar um botão para a nova página
        page_button = PageButton(user, page_index)
        page_button.clicked.connect(
            lambda: self.switch_to_page(new_page, page_button))
        page_button.setObjectName(f"page_button_{page_index}")

        # Adicionar o botão ao layout e ao dicionário
        self.page_buttons_layout.addWidget(page_button)
        self.page_buttons[page_index] = page_button

    def switch_to_page(self, page: WebView, button: PageButton):
        """Altera para a página selecionada e ajusta os estilos dos botões."""
        self.reset_style()
        self.pages.setCurrentWidget(page)
        button.selected()

    def update_page_button_number_notifications(self, page_index, number_notifications):
        """Atualiza o número de notificações de um botão específico."""
        if page_index in self.page_buttons:
            self.page_buttons[page_index].update_notifications(
                number_notifications)
            self.update_total_notifications()

    def update_total_notifications(self):
        """Atualiza o total de notificações no SysTray."""
        total_notifications = sum(
            button.number_notifications for button in self.page_buttons.values())
        SysTray.set_number_notifications(total_notifications)

    def reset_style(self):
        """Reseta o estilo de todos os botões."""
        for button in self.page_buttons.values():
            button.unselected()

    def close_pages(self):
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            page.__del__()
