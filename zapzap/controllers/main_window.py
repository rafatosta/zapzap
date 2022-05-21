from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QMoveEvent, QDesktopServices
from PyQt6.QtCore import QUrl, QSettings, QByteArray
from PyQt6 import uic
import zapzap
from zapzap.controllers.about import About


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        uic.loadUi(zapzap.abs_path+'/view/main_window.ui', self)
        self.app = parent
        self.openDialog = None

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__, self)

        # File
        self.actionQuit.triggered.connect(self.quit)

        # View
        self.actionReload_Service.triggered.connect(self.reload_Service)

        # Help
        self.actionLearn_More.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap')))
        self.actionChangelog.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap/releases')))
        self.actionSupport.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap/issues')))
        self.actionAbout_Zapzap.triggered.connect(self.openAbout_Zapzap)

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
        #self.settings.setValue("browser/zoomFactor", self.browser.zoomFactor())
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.hide()
        self.app.quit()

