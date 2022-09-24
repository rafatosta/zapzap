from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

import zapzap


class MenuBar():
    def __init__(self, mainWindow) -> None:
        # File
        mainWindow.actionSettings.triggered.connect(
            mainWindow.openSettings)
        mainWindow.actionDonations.triggered.connect(mainWindow.openDonations)
        mainWindow.actionQuit.triggered.connect(
            lambda x=None: mainWindow.closeEvent(x))

        def setKeep_background():
            # Save
            mainWindow.settings.setValue(
                "system/keep_background",  mainWindow.actionHide_on_close.isChecked())
            # Settings upadate
            mainWindow.zapSettings.keepBackground.setChecked(
                mainWindow.actionHide_on_close.isChecked())

        mainWindow.actionHide_on_close.triggered.connect(setKeep_background)

        # View
        mainWindow.actionReload_Service.triggered.connect(
            mainWindow.reload_Service)
        mainWindow.actionDefault_size_page.triggered.connect(
            mainWindow.setDefault_size_page)
        mainWindow.actionToggle_Full_Screen.triggered.connect(
            mainWindow.setFullSreen)
        mainWindow.actionZoomIn.triggered.connect(
            mainWindow.zoomIn)
        mainWindow.actionZoomOut.triggered.connect(
            mainWindow.zoomOut)
        mainWindow.actionAuto_hide_menu_bar.triggered.connect(
            mainWindow.setHideMenuBar)
        mainWindow.actionHome_page.triggered.connect(
            mainWindow.actionEsc)

        # Chat
        mainWindow.actionOpen_new_chat.triggered.connect(
            mainWindow.openNewChatPopup)

        # Help
        mainWindow.actionLearn_More.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__website__)))
        mainWindow.actionChangelog.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__releases__)))
        mainWindow.actionSupport.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__bugreport__)))
        mainWindow.actionAbout_Zapzap.triggered.connect(
            mainWindow.openAbout_Zapzap)
