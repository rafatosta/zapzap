from gettext import gettext as _
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QImage, QPixmap, QIcon
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
        if n > 0:
            #self.tray.setIcon(getIconTray(theme_icon, 'notify'))
            n = 999 if n >=1000 else n
            self.tray.setIcon(self.getIconModel(n))
        else:
            self.tray.setIcon(getIconTray(theme_icon, 'normal'))

    def getIconModel(self, size):
        svg_str = f"""<?xml version="1.0" encoding="utf-8"?>
        <svg viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
        <g>
            <circle cx="64" cy="64" fill="#d1000d" r="64" class="fill-25d366"/>
            <path d="M 95.889 31.927 C 87.427 23.454 76.176 18.789 64.188 18.783 C 39.489 18.783 19.383 38.885 19.375 63.593 C 19.365 71.456 21.428 79.183 25.356 85.995 L 19 109.217 L 42.754 102.987 C 49.325 106.563 56.688 108.438 64.17 108.439 L 64.189 108.439 C 88.888 108.439 108.99 88.335 109 63.628 C 109.006 51.656 104.347 40.396 95.889 31.927" fill="#FFFFFF" class="fill-ffffff"/>
        </g>
        <text style="fill: rgb(51, 51, 51); font-family: &quot;Segoe UI&quot;; font-size: 52px; font-weight: 700; stroke-width: 0.877864px; text-anchor: middle; text-transform: capitalize; white-space: pre;" transform="matrix(1, 0, 0, 1.278257, 0, -14.526803)" x="65" y="80.575">{size}</text>
        </svg>"""

        svg_bytes = bytearray(svg_str, encoding='utf-8')

        qimg = QImage.fromData(svg_bytes, 'SVG')
        qpix = QPixmap.fromImage(qimg)
        qicon = QIcon(qpix)
        return qicon
