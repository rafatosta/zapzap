import os
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSize
import zapzap
from zapzap.engine.browser import Browser
from zapzap.model.user import UserDAO
from zapzap.theme.builder_icon import getImageQIcon
from zapzap.view.home import Ui_Home
import shutil


class UserButton(QPushButton):

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

    def __init__(self, parent=None, user=None, id_page=None):
        super(UserButton, self).__init__()
        self.user = user
        self.home = parent
        self.id_page = id_page

        self.setFlat(True)
        self.setMinimumSize(QSize(30, 30))
        self.setMaximumSize(QSize(30, 30))

        self.browser = Browser(user.id)

        self.setIcon(getImageQIcon(svg_str=user.icon))
        self.setStyleSheet(self.styleSheet_normal)
        self.clicked.connect(self.click)

    def click(self):
        self.home.resetStyle()
        self.home.setPage(self.id_page)
        self.selected()

    def getBrowser(self):
        return self.browser

    def closeBrowser(self):
        self.browser.close()
        del self.browser

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
        for id_page, user in enumerate(self.list):
            button = UserButton(self, user, id_page)
            self.menu.addWidget(button)
            self.userStacked.insertWidget(id_page, button.getBrowser())

    def addNewUser(self, user):
        self.list.append(user)
        button = UserButton(self, user)
        self.menu.addWidget(button)
        id_page = self.userStacked.addWidget(button.getBrowser())
        button.id_page = id_page

        print(id_page)

        b = self.getUserButton(user.id)
        print('>>',b.id_page)

    def activeMenu(self):
        if len(self.list) > 1:
            self.menu.itemAt(0).widget().selected()
        else:
            self.menuUsers.hide()

    def resetStyle(self):
        for i in reversed(range(self.menu.count())):
            ub = self.menu.itemAt(i).widget()
            ub.unselected()

    def setPage(self, id_page):
        self.userStacked.setCurrentIndex(id_page)

    def getUserButton(self, idUser):
        for i in reversed(range(self.menu.count())):
            btn = self.menu.itemAt(i).widget()
            if btn.user.id == idUser:
                return btn
        return None

    def delUserPage(self, user):
        # quando fecha a janela volta as pastas
        # acredito que seja algo relacionado ao id_page userStacked
        # continuam sendo carregados mesmo após a exclusão
        try:
            # Pega o userButton do usuário
            btn = self.getUserButton(user.id)
            # Encerra o Browser
            btn.closeBrowser()
            # remove (deixa oculto pelo menos)
            self.userStacked.removeWidget(
                self.userStacked.widget(btn.id_page))
            # remove o ícone do menu
            self.menu.itemAt(btn.id_page).widget().setParent(None)
            # deleta do banco de dados
            UserDAO.delete(user.id)
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
