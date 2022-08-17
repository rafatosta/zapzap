from gettext import gettext as _
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from zapzap.controllers.main_window_components.builder_icon import getIconTray


class TrayIcon():
    def __init__(self, mainWindow) -> None:
        self.tray = QSystemTrayIcon(mainWindow)
        self.mainWindow = mainWindow
        theme_icon = self.mainWindow.settings.value(
            "notification/theme_tray", 'default', str)
        self.tray.setIcon(getIconTray(theme_icon))

        self.tray.activated.connect(mainWindow.onTrayIconActivated)

        # Itens para o menu do tray icon
        self.trayShow = QAction(_("ZapZap"), mainWindow)
        self.trayShow.triggered.connect(mainWindow.on_show)

        self.traySettings = QAction(_("Settings"), mainWindow)
        self.traySettings.triggered.connect(self.mainWindow.openTraySettings)

        self.trayExit = QAction(_("Quit"), mainWindow)
        self.trayExit.triggered.connect(lambda x = None: mainWindow.closeEvent(x))

        # Cria o Menu e adiciona as ações
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayShow)
        self.trayMenu.addAction(self.traySettings)
        self.trayMenu.insertSeparator(self.trayExit)
        self.trayMenu.addAction(self.trayExit)

        self.tray.setContextMenu(self.trayMenu)

        # Mostra o Tray na barra de status
        if (mainWindow.settings.value("system/tray_icon", True, bool)):
            self.tray.show()

    def setVisible(self, v):
        self.tray.setVisible(v)

    def showIconNotification(self, n):
        theme_icon = self.mainWindow.settings.value(
            "notification/theme_tray", 'default', str)
        n = 999 if n >= 1000 else n
        self.tray.setIcon(getIconTray(theme_icon, n))