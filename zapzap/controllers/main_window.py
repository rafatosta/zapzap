from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QMoveEvent, QDesktopServices
from PyQt6.QtCore import QUrl, QSettings, QByteArray
from PyQt6 import uic
import zapzap
from zapzap.controllers.about import About
from zapzap.controllers.main_window_components.menu_bar import MenuBar
from zapzap.controllers.main_window_components.tray_icon import TrayIcon


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        uic.loadUi(zapzap.abs_path+'/view/main_window.ui', self)
        self.app = parent
        self.openDialog = None

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__, self)

        MenuBar(self)
        TrayIcon(self)

    def reload_Service(self):
        print('f5')

    def openAbout_Zapzap(self):
        self.openDialog = About(self)
        self.openDialog.show()

    def moveEvent(self, a0: QMoveEvent) -> None:
        if self.openDialog != None:
            self.openDialog.centerPos()
        return super().moveEvent(a0)

    def loadSettings(self):
        self.restoreGeometry(self.settings.value(
            "main/geometry", QByteArray()))
        self.restoreState(self.settings.value(
            "main/windowState", QByteArray()))

        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        isStart_hide = self.settings.value("system/start_hide", False, bool)

        if isStart_system and isStart_hide:
            self.hide()
        else:
            self.show()

    def quit(self):
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.hide()
        self.app.quit()

    def closeEvent(self, event):
        """ Override the window close event.
        Save window dimensions and check if it should be hidden or closed
        """
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())

        if self.settings.value(
                "system/keep_background", True, bool):
            self.hide()
            event.ignore()
