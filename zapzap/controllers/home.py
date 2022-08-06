from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSize
from zapzap.engine.browser import Browser
from zapzap.model.user import UserDAO
from zapzap.theme.builder_icon import getImageQIcon
from zapzap.view.home import Ui_Home


class UserButton(QPushButton):

    styleSheet = """
    QPushButton {	
       qproperty-iconSize: 22px;
       
    }
    QPushButton:hover{
        background-color: rgba(0, 0, 0,0.7); 
        border-radius: 15px;
    }
    """

    def __init__(self, parent=None, user=None, id_page=None):
        super(UserButton, self).__init__()
        self.user = user
        self.home = parent
        self.id_page = id_page

        self.setFlat(True)
        self.setMinimumSize(QSize(32,32))
        self.setMaximumSize(QSize(32,32))

        self.browser = Browser(user.id)

        self.setIcon(getImageQIcon(svg_str=user.icon))
        self.setStyleSheet(self.styleSheet)
        self.clicked.connect(self.click)

    def click(self):
        self.home.userStacked.setCurrentIndex(self.id_page)

    def getBrowser(self):
        return self.browser


class Home(QWidget, Ui_Home):
    def __init__(self, parent=None):
        super(Home, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent

        self.loadUsers()

    def loadUsers(self):
        list = UserDAO.select()
        for id_page, user in enumerate(list):
            button = UserButton(self, user, id_page)
            self.menu.addWidget(button)
            self.userStacked.insertWidget(id_page, button.getBrowser())
