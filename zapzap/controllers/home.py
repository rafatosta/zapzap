import os
from PyQt6.QtWidgets import QWidget, QPushButton, QApplication
from PyQt6.QtCore import QSize
import zapzap
from zapzap.engine.browser import Browser
from zapzap.model.user import UserDAO
from zapzap.theme.builder_icon import getImageQIcon
from zapzap.view.home import Ui_Home
import shutil


class UserContainer(QPushButton):

    isSelected = False

    styleSheet_normal = """
    QPushButton {	
       qproperty-iconSize: 20px;
    }
    """

    styleSheet_hover = """
    QPushButton {	
       qproperty-iconSize: 30px;
    }
    """

    def __init__(self, parent=None, user=None):
        super(UserContainer, self).__init__()
        self.user = user
        self.home = parent

        self.qtd = 0

        self.setFlat(True)
        self.setMinimumSize(QSize(30, 30))
        self.setMaximumSize(QSize(30, 30))

        self.browser = Browser(user.id, self)

        self.setIcon(getImageQIcon(svg_str=user.icon))
        self.setStyleSheet(self.styleSheet_normal)
        self.clicked.connect(self.click)

    def showIconNotification(self, qtd):
        self.qtd = qtd
        self.setIcon(getImageQIcon(svg_str=self.user.icon, qtd=qtd))
        mainWindow = QApplication.instance().getWindow()
        mainWindow.emitNotifications()

    def click(self):
        self.home.resetStyle()
        self.home.setPage(self.browser)
        self.selected()

    def getBrowser(self):
        return self.browser

    def closeBrowser(self):
        self.browser.stop()

    ## EVENTS ##

    def selected(self):
        self.isSelected = True
        self.setStyleSheet(self.styleSheet_hover)

    def unselected(self):
        self.isSelected = False
        self.setStyleSheet(self.styleSheet_normal)

    def enterEvent(self, e):
        self.setStyleSheet(self.styleSheet_hover)

    def leaveEvent(self, e):
        if not self.isSelected:
            self.setStyleSheet(self.styleSheet_normal)


class Home(QWidget, Ui_Home):
    list = None

    def __init__(self, parent=None):
        super(Home, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent
        self.loadUsers()
        self.activeMenu()

    def loadUsers(self):
        self.list = UserDAO.select()
        for user in self.list:
            button = UserContainer(self, user)
            self.menu.addWidget(button)
            self.userStacked.addWidget(button.getBrowser())

    def addNewUser(self, user):
        self.list.append(user)
        button = UserContainer(self, user)
        self.menu.addWidget(button)
        self.userStacked.addWidget(button.getBrowser())

        self.activeMenu()

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
            print(btn.qtd)
        return qtd

    def delUserPage(self, user):
        """
        1 - desativar o browser
        2 - remover do banco
        3 - remover pasta
        """
        # quando fecha a janela volta as pastas
        # acredito que seja algo relacionado ao id_page userStacked
        # continuam sendo carregados mesmo após a exclusão
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
