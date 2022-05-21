from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl


class MenuBar():
    def __init__(self, mainWindow) -> None:
        # File
        mainWindow.actionQuit.triggered.connect(mainWindow.quit)

        # View
        mainWindow.actionReload_Service.triggered.connect(
            mainWindow.reload_Service)

        # Help
        mainWindow.actionLearn_More.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap')))
        mainWindow.actionChangelog.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap/releases')))
        mainWindow.actionSupport.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap/issues')))
        mainWindow.actionAbout_Zapzap.triggered.connect(
            mainWindow.openAbout_Zapzap)
