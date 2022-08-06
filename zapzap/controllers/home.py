from PyQt6.QtWidgets import QWidget
from zapzap.view.home import Ui_Home


class Home(QWidget, Ui_Home):
    def __init__(self, parent=None):
        super(Home, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent
