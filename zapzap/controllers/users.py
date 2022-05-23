from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView
import zapzap
from zapzap.controllers.zapDialog import ZapDialog
import zapzap.model.users_model as user_db


class Users(ZapDialog):
    def __init__(self, container_list):
        super().__init__(zapzap.abs_path+'/view/users.ui')
        self.container_list = container_list
        self.nameLineEdit.textEdited.connect(self.text_edited)
        self.pbAdd.clicked.connect(self.addUser)
        self.clear()

        # evento da tabela
        self.tableWidget.clicked.connect(self.selectItemTable)

        # load users
        self.loadUsers()

    def loadUsers(self):
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.setRowCount(0)
        for user in self.container_list:
            rowCount = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowCount)

            id = QTableWidgetItem(user.nameSpace)
            nome = QTableWidgetItem(user.name)

            self.tableWidget.setItem(rowCount, 0, id)
            self.tableWidget.setItem(rowCount, 1, nome)

    def selectItemTable(self):
        row = self.tableWidget.currentRow()
        print(row)

    def text_edited(self, s):
        if len(s) > 0:
            self.pbAdd.setEnabled(True)
        else:
            self.pbAdd.setEnabled(False)

    def addUser(self):
        new_container = user_db.insert(self.nameLineEdit.text())
        print(new_container.name)
        self.loadUsers()

        self.clear()
    
    def removeUser(self):
        pass

    def clear(self):
        self.pbAdd.setEnabled(False)
        self.pbRemove.hide()
        self.nameLineEdit.clear()


# Ao adicionar: verificar se existe outro com o mesmo NOME (não do storageName)
# Ao remover: apagar a pasta do QProfile a partir do storageName
# Ao Editar: substituir apenas o nome (não o storageName)

# Ao final de qualquer operação: Atualizar a mainWindow.
