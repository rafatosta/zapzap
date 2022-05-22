from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl


class MenuBar():
    def __init__(self, mainWindow) -> None:
        # File
        mainWindow.actionQuit.triggered.connect(mainWindow.quit)
        mainWindow.actionHide_on_close.triggered.connect(
            lambda: mainWindow.settings.setValue(
                "system/keep_background",  mainWindow.actionHide_on_close.isChecked()))

        # View
        mainWindow.actionReload_Service.triggered.connect(
            mainWindow.reload_Service)
        mainWindow.actionOpen_Quick_Switch.triggered.connect(
            mainWindow.open_Quick_Switch)
        mainWindow.actionToggle_Full_Screen.triggered.connect(
            mainWindow.setFullSreen)
        mainWindow.actionAuto_hide_menu_bar.triggered.connect(
            mainWindow.setHideMenuBar)

        # Users
        mainWindow.actionAdd_new_user.triggered.connect(
            mainWindow.openNewUserDialog)

        # Help
        mainWindow.actionLearn_More.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap')))
        mainWindow.actionChangelog.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap/releases')))
        mainWindow.actionSupport.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/rafatosta/zapzap/issues')))
        mainWindow.actionAbout_Zapzap.triggered.connect(
            mainWindow.openAbout_Zapzap)
