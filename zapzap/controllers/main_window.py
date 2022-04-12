from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from zapzap.controllers.drawer import Drawer
from zapzap.engine.browser import Browser
from zapzap import theme_light_path, theme_dark_path, tray_path


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app

        self.isTheme = True
        # Define tamanho mínimo para a janela
        self.setMinimumSize(800, 600)

        # rotina para definição do Tray
        self.createTrayIcon()

        # rotina para criação do WebView que irá carregar a página do whatsapp
        self.createWebEngine()

        # cria o menu drawer
        self.createDrawer()

        # aplica o estilo inicial
        self.toggle_stylesheet()

    def createDrawer(self):
        self.drawer = Drawer(self)
        self.drawer.maximum_width = self.width()
        self.drawer.raise_()

    def createTrayIcon(self):
        # Criando o tray icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(tray_path))
        self.tray.activated.connect(self.onTrayIconActivated)

        # Itens para o menu do tray icon
        self.trayShow = QAction('Show', self)
        self.trayShow.triggered.connect(self.on_show)

        self.trayExit = QAction('Exit', self)
        self.trayExit.triggered.connect(lambda: self.app.quit())

        # Cria o Menu e adiciona as ações
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayShow)
        self.trayMenu.addAction(self.trayExit)

        self.tray.setContextMenu(self.trayMenu)

        # Mostra o Tray na barra de status
        self.tray.show()

    def createWebEngine(self):
        self.browser = Browser(self)
        self.browser.doReload()
        self.setCentralWidget(self.browser)

    # Abrindo o webapp do system tray.
    def on_show(self):
        self.show()
        self.app.activateWindow()  # ao mostrar move a janela para a área de trabalho atual

    # Evento para mostrar e ocultar a janela com apenas dois clique ou botão do meio no tray icon. Com um click abre o menu.
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.on_show()
            self.app.activateWindow()

    # Evento ao fechar a janela.
    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def resizeEvent(self, event):
        self.drawer.setFixedHeight(self.height() - self.drawer.pos().y())
        self.drawer.maximum_width = self.width()
        super().resizeEvent(event)

    def toggle_stylesheet(self):
        if self.isTheme:
            path = theme_light_path
            self.browser.whats.setTheme('light')
            self.drawer.settings.night_mode.setChecked(False)
            self.isTheme = False
        else:
            path = theme_dark_path
            self.browser.whats.setTheme('dark')
            self.drawer.settings.night_mode.setChecked(True)
            self.isTheme = True

        with open(path, 'r') as f:
            style = f.read()

        # Set the stylesheet of the application
        self.app.setStyleSheet(style)

    # Mapeamento dos atalhos
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F5:
            self.browser.doReload()
        if e.key() == Qt.Key.Key_F1:
            self.toggle_stylesheet()
