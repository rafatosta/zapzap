from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
import zapzap


class SettingsNew(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        uic.loadUi(zapzap.abs_path+'/view/settings_new.ui', self)
        self.mainWindow = parent

        self.btn_back.clicked.connect(self.actionBack)

    def actionBack(self):
        self.mainWindow.setHideMenuBar()
        self.mainWindow.stackedWidget.setCurrentIndex(0)
