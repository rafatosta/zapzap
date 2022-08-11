import os
import shutil
from PyQt6.QtWidgets import QWidget
from zapzap.controllers.user_container import UserContainer
from zapzap.model.user import UserDAO
from zapzap.view.home import Ui_Home
import zapzap


class Home(QWidget, Ui_Home):
    list = None

    def __init__(self, parent=None):
        super(Home, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent
        self.loadUsers()
        self.activeMenu()
        self.updateShortcuts()

    def loadUsers(self):
        self.list = UserDAO.select()
        for user in self.list:
            button = UserContainer(self, user)
            self.menu.addWidget(button)
            self.userStacked.addWidget(button.getBrowser())

    def updateShortcuts(self):
        for i in range(self.userStacked.count()):
            btn = self.menu.itemAt(i).widget()
            btn.setShortcut(f'Ctrl+{i+1}')

    def addNewUser(self, user):
        self.list.append(user)
        button = UserContainer(self, user)
        self.menu.addWidget(button)
        self.userStacked.addWidget(button.getBrowser())

        self.activeMenu()
        self.updateShortcuts()

    def activeMenu(self):
        if len(self.list) > 1:
            self.menuUsers.show()
            self.menu.itemAt(0).widget().selected()
        else:
            self.menuUsers.hide()

    def resetStyle(self):
        for i in reversed(range(self.menu.count())):
            ub = self.menu.itemAt(i).widget()
            ub.unselected()

    def setPage(self, browser):
        self.userStacked.setCurrentWidget(browser)

    def getUserContainer(self, idUser):
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            if btn.user.id == idUser:
                return btn, i
        return None

    def getSizeNotifications(self) -> int:
        qtd = 0
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            qtd += btn.qtd
        return qtd

    def setThemePages(self, isNight_mode):
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn.setThemePage(isNight_mode)

    def setZoomFactor(self, factor=None):
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.setZoomFactorPage(factor)

    def saveSettings(self):
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn.saveSettings()

    def reloadPage(self):
        self.userStacked.currentWidget().doReloadPage()

    def delUserPage(self, user):
        # quando fecha a janela volta as pastas, pois há um delay ao encerrar a page.
        try:
            # Pega o UserContainer do usuário
            return_btn = self.getUserContainer(user.id)
            btn = return_btn[0]
            id_btn = return_btn[1]

            # remove (deixa oculto pelo menos)
            self.userStacked.removeWidget(btn.browser)

            # remove o ícone do menu
            self.menu.itemAt(id_btn).widget().setParent(None)

            # Encerra o Browser
            btn.closeBrowser()

            # deleta do banco de dados
            UserDAO.delete(user.id)

            # deleta da lista
            for u in self.list:
                if u.id == user.id:
                    self.list.remove(u)

            # Apaga pasta de cache do usuário
            path = os.path.join(zapzap.path_storage, str(user.id))
            shutil.rmtree(path, ignore_errors=True)
        except OSError as error:
            print(error)
            print("File path can not be removed")
        else:
            print("% s removed successfully" % path)
        finally:
            self.activeMenu()
            self.updateShortcuts()
