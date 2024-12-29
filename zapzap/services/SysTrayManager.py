from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon, QDesktopServices
from PyQt6.QtCore import QUrl

from gettext import gettext as _

from zapzap.resources.TrayIcon import TrayIcon
from zapzap import __donationPage__


class SysTrayManager():

    _tray: QSystemTrayIcon = None
    icon: QIcon = TrayIcon.Type.Default

    @staticmethod
    def show():
        if not SysTrayManager._tray:
            SysTrayManager.__new_instance()

        SysTrayManager._tray.show()

    @staticmethod
    def hide():
        if not SysTrayManager._tray:
            raise RuntimeError(
                "QSystemTrayIcon não existente em QApplication.")

        SysTrayManager._tray.hide()

    @staticmethod
    def set_number_notifications(number_notifications):
        SysTrayManager._tray.setIcon(TrayIcon.getIcon(
            SysTrayManager.icon, number_notifications))

    @staticmethod
    def __new_instance():
        main_window = QApplication.instance().getWindow()

        SysTrayManager._tray = QSystemTrayIcon(main_window)
        SysTrayManager._tray.setIcon(TrayIcon.getIcon(SysTrayManager.icon))

        # Persistência dos itens e ações
        SysTrayManager._actions = {
            "show": QAction(_("Show")),
            "settings": QAction(_("Settings")),
            "donation": QAction(_("Donation")),
            "exit": QAction(_("Quit")),
        }

        # Conexões dos sinais
        SysTrayManager._actions["show"].triggered.connect(
            main_window.show_window)
        SysTrayManager._actions["donation"].triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__)))
        SysTrayManager._actions["settings"].triggered.connect(
            main_window.open_settings)
        SysTrayManager._actions["exit"].triggered.connect(
            main_window.closeEvent)

        # Criação do menu persistente
        SysTrayManager._trayMenu = QMenu()
        SysTrayManager._trayMenu.addAction(SysTrayManager._actions["show"])
        SysTrayManager._trayMenu.addAction(SysTrayManager._actions["settings"])
        SysTrayManager._trayMenu.addAction(SysTrayManager._actions["donation"])
        SysTrayManager._trayMenu.addAction(SysTrayManager._actions["exit"])
        SysTrayManager._trayMenu.insertSeparator(SysTrayManager._actions["exit"])
        SysTrayManager._trayMenu.insertSeparator(SysTrayManager._actions["settings"])

        SysTrayManager._tray.setContextMenu(SysTrayManager._trayMenu)
