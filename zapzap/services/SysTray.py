from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon, QDesktopServices
from PyQt6.QtCore import QUrl

from gettext import gettext as _

from zapzap.resources.TrayIcon import TrayIcon
from zapzap import __donationPage__


class SysTray():

    _tray: QSystemTrayIcon = None
    icon: QIcon = TrayIcon.Type.Default

    @staticmethod
    def show():
        if not SysTray._tray:
            SysTray.__new_instance()

        SysTray._tray.show()

    @staticmethod
    def hide():
        if not SysTray._tray:
            raise RuntimeError(
                "QSystemTrayIcon não existente em QApplication.")

        SysTray._tray.hide()

    @staticmethod
    def set_number_notifications(number_notifications):
        SysTray._tray.setIcon(TrayIcon.getIcon(
            SysTray.icon, number_notifications))

    @staticmethod
    def __new_instance():
        main_window = QApplication.instance().getWindow()

        SysTray._tray = QSystemTrayIcon(main_window)
        SysTray._tray.setIcon(TrayIcon.getIcon(SysTray.icon))

        # Persistência dos itens e ações
        SysTray._actions = {
            "show": QAction(_("Show")),
            "settings": QAction(_("Settings")),
            "donation": QAction(_("Donation")),
            "exit": QAction(_("Quit")),
        }

        # Conexões dos sinais
        SysTray._actions["show"].triggered.connect(
            main_window.show_window)
        SysTray._actions["donation"].triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__)))
        SysTray._actions["settings"].triggered.connect(
            lambda: print("Signal: actionSettings"))
        SysTray._actions["exit"].triggered.connect(
            main_window.closeEvent)

        # Criação do menu persistente
        SysTray._trayMenu = QMenu()
        SysTray._trayMenu.addAction(SysTray._actions["show"])
        SysTray._trayMenu.addAction(SysTray._actions["settings"])
        SysTray._trayMenu.addAction(SysTray._actions["donation"])
        SysTray._trayMenu.addAction(SysTray._actions["exit"])
        SysTray._trayMenu.insertSeparator(SysTray._actions["exit"])
        SysTray._trayMenu.insertSeparator(SysTray._actions["settings"])

        SysTray._tray.setContextMenu(SysTray._trayMenu)
