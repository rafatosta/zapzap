from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSize
from zapzap.engine.browser import Browser
from zapzap.model.user import UserDAO
from zapzap.theme.builder_icon import getImageQIcon
from zapzap.view.home import Ui_Home


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
    def __init__(self, parent=None):
        super(Home, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent

        self.loadUsers()

        self.menu.itemAt(0).widget().selected()

    def loadUsers(self):
        list = UserDAO.select()
        for id_page, user in enumerate(list):
            button = UserButton(self, user, id_page)
            self.menu.addWidget(button)
            self.userStacked.insertWidget(id_page, button.getBrowser())

    def resetStyle(self):
        for i in reversed(range(self.menu.count())):
            ub = self.menu.itemAt(i).widget()
            ub.unselected()

    def setPage(self, id_page):
        self.userStacked.setCurrentIndex(id_page)
