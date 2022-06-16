
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from zapzap import getIconTray


class TrayIcon():
    def __init__(self, mainWindow) -> None:
        self.tray = QSystemTrayIcon(mainWindow)
        self.mainWindow = mainWindow
        theme_icon = self.mainWindow.settings.value(
            "notification/theme_tray", 'default', str)
        self.tray.setIcon(getIconTray(theme_icon, 'normal'))

        self.tray.activated.connect(mainWindow.onTrayIconActivated)

        # Itens para o menu do tray icon
        self.trayShow = QAction('Show', mainWindow)
        self.trayShow.triggered.connect(mainWindow.on_show)

        #self.traySettings = QAction('Zapzap Settings', self)
        # self.traySettings.triggered.connect(self.on_settings)

        self.trayExit = QAction('Exit', mainWindow)
        self.trayExit.triggered.connect(mainWindow.quit)

        # Cria o Menu e adiciona as ações
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayShow)
        # self.trayMenu.addAction(self.traySettings)
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
        if n > 0:
            self.tray.setIcon(getIconTray(theme_icon, 'notify'))
        else:
            self.tray.setIcon(getIconTray(theme_icon, 'normal'))
