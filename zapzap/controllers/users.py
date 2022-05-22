from PyQt6.QtCore import QSettings
import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class Users(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/users.ui')

        self.users_sgs = QSettings(zapzap.__appname__, 'users')

        self.nameLineEdit.textEdited.connect(self.text_edited)
        self.pbAdd.clicked.connect(self.addUser)
        self.pbAdd.setEnabled(False)
        self.pbRemove.hide()
        self.loadUsers()

    def loadUsers(self):
        self.users_sgs.beginGroup("users")
        self.listWidget.clear()
        self.list_user = self.users_sgs.allKeys()
        print(self.list_user)
        for user in self.list_user:
            self.listWidget.addItem(self.users_sgs.value(user, dict)['name'])

        self.users_sgs.endGroup()

    def text_edited(self, s):
        if len(s) > 0:
            self.pbAdd.setEnabled(True)
        else:
            self.pbAdd.setEnabled(False)

    def addUser(self):
        self.users_sgs.beginGroup("users")
        storageName = self.nameLineEdit.text()
        name = self.nameLineEdit.text()
        self.users_sgs.setValue(
            storageName, {'storageName': storageName,
                          'name': name})
        self.users_sgs.endGroup()

        self.nameLineEdit.clear()
        self.pbAdd.setEnabled(False)

        self.loadUsers()

# Ao adicionar, verificar se existe outro com o mesmo NOME (não do storageName)
# Ao remover, apagar a pasta do QProfile a partir do storageName
# Ao Editar, substituir apenas o nome (não o storageName)