from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from zapzap.browser import Browser


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app

        # Define tamanho mínimo para a janela
        self.setMinimumSize(800, 600)

        # rotina para criação do WebView que irá carregar a página do whatsapp
        self.createWebEngine()

        # rotina para definição do Tray
        self.createTrayIcon()

    def createTrayIcon(self):
        # Criando o tray icon
        self.tray = QSystemTrayIcon()
        self.tray.activated.connect(self.onTrayIconActivated)
        self.tray.setIcon(self.view.icon())

        # Itens para o menu do tray icon
        self.trayHide = QAction('Hide', self)
        self.trayShow = QAction('Show', self)
        self.trayExit = QAction('Exit', self)

        # Funções para as opções do menu do tray icon
        self.trayHide.triggered.connect(self.on_hide)
        self.trayShow.triggered.connect(self.on_show)
        self.trayExit.triggered.connect(lambda: self.app.quit())

        # Cria o Menu e adiciona as ações
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)

        self.tray.setContextMenu(self.trayMenu)

        # Mostra o Tray na barra de status
        self.tray.show()

    def createWebEngine(self):
        self.view = Browser(self)
        self.setCentralWidget(self.view)

    # Abrindo o webapp do system tray.
    def on_show(self):
        self.show()
        self.trayMenu.clear()  # Alterando as opções do menu do tray icon
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)
        self.app.activateWindow() #ao mostrar move a janela para a área de trabalho atual

    # Minimizando para o system tray.
    def on_hide(self):
        # Evitando que o programa minimize ao invés de maximizar ao reabri-lo
        if self.isMinimized():
            self.show()

        self.hide()
        self.trayMenu.clear()  # Alterando as opções do menu do tray icon
        self.trayMenu.addAction(self.trayShow)
        self.trayMenu.addAction(self.trayExit)

    # Evento para mostrar e ocultar a janela com apenas dois clique ou botão do meio no tray icon. Com um click abre o menu.
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            if self.isHidden():
                self.on_show()
            else:
                self.on_hide()

    # Evento ao fechar a janela.
    def closeEvent(self, event):
        self.hide()
        self.on_hide()
        event.ignore()
