from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from zapzap.view.account_page import Ui_Account
from zapzap.controllers.card_user import User, CardUser
from zapzap.model.user import UserDAO
from zapzap.theme.builder_icon import getImageQPixmap, getNewIconSVG
import zapzap


class Account(QWidget, Ui_Account):

    LIMITE_USERS = 9

    emitDisableUser = pyqtSignal(User)
    emitDeleteUser = pyqtSignal(User)
    emitEditUser = pyqtSignal(User)
    emitNewtUser = pyqtSignal(User)

    def __init__(self):
        super(Account, self).__init__()
        self.setupUi(self)
        self.loadUsers()

        self.btnNewUser.clicked.connect(self.newUserbuttonClick)

    def loadUsers(self):
        """def clear():
            for i in reversed(range(self.usersList.count())):
                self.usersList.itemAt(i).widget().setParent(None)
        clear()"""
        list = UserDAO.select(False)
        for user in list:
            self.usersList.addWidget(self.getNewCardUser(user))

    def updateListUser(self, user: User):
        self.usersList.addWidget(self.getNewCardUser(user))

    def getNewCardUser(self, user) -> CardUser:
        card = CardUser(user)
        card.emitDisableUser.connect(lambda: self.emitDisableUser.emit(user))
        card.emitDeleteUser.connect(lambda: self.emitDeleteUser.emit(user))
        card.emitEditUser.connect(lambda: self.emitEditUser.emit(user))
        return card

    def newUserbuttonClick(self):
        if self.usersList.count() < self.LIMITE_USERS:
            # Cria o usuário
            user = User(
                name='', icon=getNewIconSVG())
            # insere no banco de dados e recebe o user com o ID
            user = UserDAO.add(user)
            # Insere  o card
            self.usersList.addWidget(self.getNewCardUser(user))
            # Informa a criação do usuário
            self.emitNewtUser.emit(user)

    def updateUsersShortcuts(self):
        count = 1
        for i in range(self.usersList.count()):
            card = self.usersList.itemAt(i).widget()
            if card.user.enable:
                card.key.setText(f'Ctrl+{count}')
                count += 1
            else:
                card.key.setText('')
