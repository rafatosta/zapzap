from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMenu

from zapzap.controllers.CardUser import CardUser
from zapzap.models.User import User


class PageAccount(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_account.ui", self)

        self._load_users()

    def _load_users(self):
        """Carrega os usuários e cria páginas correspondentes."""
        self.user_list = User.select()
        for user in self.user_list:
            print(user)
            self.user_list_layout.addWidget(CardUser(user))
