
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from zapzap import tray_path, tray_symbolic_path


class TrayIcon():
    def __init__(self, mainWindow) -> None:
        self.tray = QSystemTrayIcon(mainWindow)
       
        isTraySymbolic = mainWindow.settings.value(
            "notification/symbolic_icon", True, bool)
        if isTraySymbolic:
            self.tray.setIcon(QIcon(tray_symbolic_path))
        else:
            self.tray.setIcon(QIcon(tray_path))
        self.tray.activated.connect(mainWindow.onTrayIconActivated)

        # Itens para o menu do tray icon
        self.trayShow = QAction('Show', mainWindow)
        self.trayShow.triggered.connect(mainWindow.on_show)

        #self.traySettings = QAction('Zapzap Settings', self)
        #self.traySettings.triggered.connect(self.on_settings)

        self.trayExit = QAction('Exit', mainWindow)
        self.trayExit.triggered.connect(mainWindow.quit)

        # Cria o Menu e adiciona as ações
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayShow)
        #self.trayMenu.addAction(self.traySettings)
        self.trayMenu.insertSeparator(self.trayExit)
        self.trayMenu.addAction(self.trayExit)

        self.tray.setContextMenu(self.trayMenu)

        # Mostra o Tray na barra de status
        self.tray.show()