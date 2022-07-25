from gettext import gettext as _
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize

from zapzap.controllers.main_window_components.builder_icon import getIconTray_2


class TrayIcon():
    def __init__(self, mainWindow) -> None:
        self.tray = QSystemTrayIcon(mainWindow)
        self.mainWindow = mainWindow
        theme_icon = self.mainWindow.settings.value(
            "notification/theme_tray", 'default', str)
        self.tray.setIcon(getIconTray_2(theme_icon))

        self.tray.activated.connect(mainWindow.onTrayIconActivated)

        # Itens para o menu do tray icon
        self.trayShow = QAction(_("View"), mainWindow)
        self.trayShow.triggered.connect(mainWindow.on_show)

        self.traySettings = QAction(_("Settings"), mainWindow)
        self.traySettings.triggered.connect(self.mainWindow.openSettings)

        self.trayExit = QAction(_("Quit"), mainWindow)
        self.trayExit.triggered.connect(mainWindow.quit)

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
        self.tray.setIcon(getIconTray_2(theme_icon, n))

    def getIconModel(self, size):

        if len(str(size)) == 1:
            data = dict(width=60, x=68, text=size)
        elif len(str(size)) == 2:
            data = dict(width=88, x=40, text=size)
        else:
            data = dict(width=128, x=0, text=size)

        svg_str = f"""<?xml version="1.0" encoding="utf-8"?>
            <svg viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
                <circle cx="64" cy="64" fill="#00a82b" r="64" class="fill-25d366"/>
                <path d="M92.346 35.49c-7.522-7.53-17.523-11.678-28.179-11.683-21.954 0-39.826 17.868-39.833 39.831a39.743 39.743 0 0 0 5.316 19.913L24 104.193l21.115-5.538a39.837 39.837 0 0 0 19.036 4.847h.017c21.954 0 39.823-17.871 39.832-39.833.005-10.642-4.136-20.65-11.654-28.179M64.168 96.774h-.013a33.062 33.062 0 0 1-16.853-4.614l-1.209-.718-12.53 3.287 3.343-12.216-.787-1.256a32.998 32.998 0 0 1-5.062-17.619c.006-18.253 14.859-33.104 33.121-33.104 8.844.002 17.155 3.451 23.407 9.71 6.251 6.258 9.691 14.575 9.689 23.422-.006 18.256-14.859 33.108-33.106 33.108m18.16-24.795c-.996-.499-5.889-2.904-6.802-3.239-.913-.332-1.574-.497-2.238.499s-2.571 3.239-3.153 3.903c-.58.664-1.16.748-2.156.249s-4.202-1.549-8.001-4.941c-2.96-2.637-4.958-5.899-5.538-6.895s-.062-1.533.437-2.03c.448-.446.996-1.162 1.493-1.744.497-.582.663-.997.995-1.66.332-.664.167-1.245-.083-1.743-.25-.499-2.24-5.398-3.068-7.391-.809-1.941-1.629-1.678-2.239-1.708a41.082 41.082 0 0 0-1.908-.036c-.663 0-1.742.249-2.654 1.246-.911.996-3.483 3.403-3.483 8.304 0 4.898 3.566 9.632 4.064 10.295.498.663 7.018 10.718 17.002 15.029a57.94 57.94 0 0 0 5.674 2.097c2.384.759 4.554.65 6.27.394 1.912-.285 5.888-2.407 6.719-4.732.829-2.324.829-4.316.578-4.732-.251-.417-.915-.666-1.909-1.165" fill="#ffffff" class="fill-ffffff"/>
                <rect x="{data['x']}" y="55.704" width="{data['width']}" height="72.263" style="fill: rgb(255, 0, 0); stroke: rgb(255, 0, 0);" rx="19.653" ry="19.653"/>
                <text style="fill: rgb(255, 255, 255); font-family: Arial, sans-serif; font-size: 70px; font-weight: 700; text-anchor: end; white-space: pre;" x="122.63" y="120">{data['text']}</text>
            </svg>
        """

        svg_bytes = bytearray(svg_str, encoding='utf-8')

        qimg = QImage.fromData(svg_bytes, 'SVG')

        qpix = QPixmap.fromImage(qimg)
        qicon = QIcon(qpix.scaled(QSize(128, 128)))
        return qicon
