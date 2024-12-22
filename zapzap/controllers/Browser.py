from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QPushButton

from zapzap.controllers.PageButton import PageButton
from zapzap.controllers.WebView import WebView
from zapzap.models.User import User
from zapzap.controllers.DynamicPage import DynamicPage
from zapzap.services.SysTray import SysTray


class Browser(QWidget):

    page_count = 0  # Contador de páginas
    page_buttons = {}  # Dicionário para mapear botões às páginas

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_browser.ui", self)

        self.load_users()

    def load_users(self):
        self.user_list = User.select()
        for user in self.user_list:
            print(user.id)
            self.add_page(user)

    def add_page(self, user: User):
        """Adiciona uma nova página e um botão correspondente."""
        self.page_count += 1
        page_index = self.page_count

        # Criar uma nova página
        # new_page = DynamicPage(page_index)
        new_page = WebView(user, page_index)

        # Conectar o sinal da página ao método de atualização de botão
        new_page.update_button_signal.connect(
            self.update_page_button_number_notifications)

        # Adicionar a nova página ao QStackedWidget
        self.pages.addWidget(new_page)

        # Criar um botão para a nova página
        page_button = PageButton(user, page_index)
        page_button.clicked.connect(
            lambda: self.pages.setCurrentWidget(new_page))
        page_button.setObjectName(f"page_button_{page_index}")

        # Adicionar o botão ao layout e ao dicionário de mapeamento
        self.page_buttons_layout.addWidget(page_button)
        self.page_buttons[page_index] = page_button

    def update_page_button_number_notifications(self, page_index, number_notifications):
        if page_index in self.page_buttons:
            button = self.page_buttons[page_index]
            button.update_notifications(number_notifications)

            self.get_number_notifications()

    def get_number_notifications(self):
        sum = 0
        for page_button in self.page_buttons.values():
            sum += page_button.number_notifications
        print('total:', sum)
        SysTray.set_number_notifications(sum)
