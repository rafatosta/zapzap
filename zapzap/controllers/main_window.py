from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSettings, QByteArray
import zapzap
from zapzap.controllers.drawer import Drawer
from zapzap.engine.browser import Browser
from zapzap import theme_light_path, theme_dark_path, tray_path


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app

        # Define tamanho mínimo para a janela
        self.setMinimumSize(800, 600)

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__, self)

        # rotina para definição do Tray
        self.createTrayIcon()

        # rotina para criação do WebView que irá carregar a página do whatsapp
        self.createWebEngine()

        # cria o menu drawer
        self.createDrawer()

        # Restore Settings
        self.readSettings()

    def readSettings(self):
        self.restoreGeometry(self.settings.value(
            "main/geometry", QByteArray()))
        self.restoreState(self.settings.value(
            "main/windowState", QByteArray()))

        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        isStart_hide = self.settings.value("system/start_hide", False, bool)

        if isStart_system and isStart_hide:
            self.hide()
        else:
            self.show()

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

        self.traySettings = QAction('Zapzap Settings', self)
        self.traySettings.triggered.connect(self.on_settings)

        self.trayExit = QAction('Exit', self)
        self.trayExit.triggered.connect(self.closeApp)

        # Cria o Menu e adiciona as ações
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayShow)
        self.trayMenu.addAction(self.traySettings)
        self.trayMenu.insertSeparator(self.trayExit)
        self.trayMenu.addAction(self.trayExit)

        self.tray.setContextMenu(self.trayMenu)

        # Mostra o Tray na barra de status
        self.tray.show()

    def on_settings(self):
        if self.drawer.isOpen:
            self.drawer.onToggled()

        self.show()
        self.app.activateWindow()

    def createWebEngine(self):
        self.browser = Browser(self)
        self.browser.setZoomFactor(self.settings.value(
            "browser/zoomFactor", 1.0, float))
        self.browser.doReload()

        self.setCentralWidget(self.browser)

    def closeApp(self):
        # Save zoomFactor for browser
        self.settings.setValue("browser/zoomFactor", self.browser.zoomFactor())
        self.app.quit()

    # Abrindo o webapp do system tray.
    def on_show(self):
        self.readSettings()
        if self.app.activeWindow() != None:  # Se a janela estiver em foco será escondida
            self.hide()
        else:  # Caso não esteja, será mostrada
            self.show()
            self.app.activateWindow()

    # Evento para mostrar e ocultar a janela com apenas dois clique ou botão do meio no tray icon. Com um click abre o menu.
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.on_show()
            self.app.activateWindow()

    # Evento ao fechar a janela.
    def closeEvent(self, event):
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())

        keepBackgrounf = self.settings.value(
            "system/keep_background", True, bool)
        if keepBackgrounf:
            self.hide()
            event.ignore()

    def resizeEvent(self, event):
        self.drawer.setFixedHeight(self.height() - self.drawer.pos().y())
        self.drawer.maximum_width = self.width()
        super().resizeEvent(event)

    def toggle_stylesheet(self, isNight_mode):
        if isNight_mode:
            path = theme_dark_path
        else:
            path = theme_light_path

        self.browser.whats.setTheme(isNight_mode)
        with open(path, 'r') as f:
            style = f.read()

        # Set the stylesheet of the application
        self.app.setStyleSheet(style)

    # Mapeamento dos atalhos
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F5:
            self.browser.doReload()
