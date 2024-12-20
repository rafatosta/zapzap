from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from gettext import gettext as _


class SysTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_menu()

        self.show()

    def setup_menu(self):
        # Itens para o menu do tray icon
        self.actionShow = QAction(_("ZapZap"))
        self.actionSettings = QAction(_("Settings"))
        self.actionExit = QAction(_("Quit"))

        # Signals
        self.actionShow.triggered.connect(lambda: print("Signal: actionShow "))
        self.actionSettings.triggered.connect(lambda: print("Signal: actionSettings "))
        self.actionExit.triggered.connect(lambda: print("Signal: actionExit "))

        # Menu
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.actionShow)
        self.trayMenu.addAction(self.actionSettings)
        self.trayMenu.addAction(self.actionExit)
        self.trayMenu.insertSeparator(self.actionExit)

        self.setContextMenu(self.trayMenu)
