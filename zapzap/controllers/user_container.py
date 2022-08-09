from PyQt6.QtWidgets import QPushButton, QApplication
from PyQt6.QtCore import QSize
from zapzap.theme.builder_icon import getImageQIcon
from zapzap.engine.browser import Browser


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
        self.browser.setZoomFactor(user.zoomFactor)
        self.browser.doReload()

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
