from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6 import uic
import zapzap


class SettingsNew(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        uic.loadUi(zapzap.abs_path+'/view/settings_new.ui', self)
        self.mainWindow = parent

        self.btn_home.clicked.connect(lambda: self.mainWindow.stackedWidget.setCurrentIndex(0))

        self.btn_system.clicked.connect(self.buttonClick)
        self.btn_appearance.clicked.connect(self.buttonClick)
        self.btn_notifications.clicked.connect(self.buttonClick)
        self.btn_about.clicked.connect(self.buttonClick)

        self.stackedWidget.setCurrentIndex(0)
        self.btn_system.setStyleSheet(
            self.selectMenu(self.btn_system.styleSheet()))

    def buttonClick(self):
        btn = self.sender()  # returns a pointer to the object that sent the signal
        btnName = btn.objectName()
        print(btnName)

        self.resetStyle(btnName)
        if btnName == 'btn_system':
            self.stackedWidget.setCurrentIndex(0)
            self.btn_system.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_appearance':
            self.stackedWidget.setCurrentIndex(1)
            self.btn_appearance.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_notifications':
            self.stackedWidget.setCurrentIndex(2)
            self.btn_notifications.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_about':
            self.stackedWidget.setCurrentIndex(3)
            self.btn_about.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

    # SELECT/DESELECT MENU
    # ///////////////////////////////////////////////////////////////
    # SELECT
    # MENU SELECTED STYLESHEET
    MENU_SELECTED_STYLESHEET = """
    background-color: rgb(192, 191, 188);
    border-color: rgb(192, 191, 188);
    """

    def selectMenu(self, getStyle):
        select = getStyle + self.MENU_SELECTED_STYLESHEET
        return select

    # DESELECT
    def deselectMenu(self, getStyle):
        deselect = getStyle.replace(self.MENU_SELECTED_STYLESHEET, "")
        return deselect

    # RESET SELECTION
    def resetStyle(self, widget):
        for w in self.menu.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(self.deselectMenu(w.styleSheet()))