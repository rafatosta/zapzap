from PyQt6.QtWidgets import QWidget, QApplication

from zapzap.controllers.CardUser import CardUser
from zapzap.models.User import User
from zapzap.services.AlertManager import AlertManager
from zapzap.views.ui_page_account import Ui_PageAccount


class PageAccount(QWidget, Ui_PageAccount):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Inicializa a interface e carrega os usuários
        self._load_users()

        # Conecta o botão de adicionar novo usuário ao método correspondente
        self.btn_new_user.clicked.connect(self._new_user)

    def _load_users(self):
        """Carrega os usuários e cria cards correspondentes."""
        self.user_list = User.select()
        for user in self.user_list:
            self.user_list_layout.addWidget(CardUser(user))

    def _new_user(self):
        """Adiciona um novo usuário, se o limite não for atingido."""
        new_user = User.create_new_user()

        if new_user:
            # Adiciona o card do novo usuário à interface
            self.user_list_layout.addWidget(CardUser(new_user))

            # Atualiza o navegador com o novo usuário
            QApplication.instance().getWindow().browser.add_new_user(new_user)
        else:
            AlertManager.limit_users(self)
