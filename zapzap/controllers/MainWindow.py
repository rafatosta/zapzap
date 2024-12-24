from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QByteArray

from zapzap.controllers.Browser import Browser
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager


class MainWindow(QMainWindow):
    """
    Classe principal para a interface do aplicativo.
    Controla a janela principal, incluindo o menu e interações com widgets centrais.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_mainwindow.ui", self)

        self.is_fullscreen = False  # Controle do estado de tela cheia
        self.browser = Browser()  # Inicialização do navegador

        self.init_menu_actions()

        self.setCentralWidget(self.browser)

    def init_settings(self):
        # Restaurar configurações
        self.restoreGeometry(SettingsManager.get(
            "main/geometry", QByteArray()))
        self.restoreState(SettingsManager.get(
            "main/windowState", QByteArray()))

        SysTrayManager.show()  # Exibe o SysTray

    def init_menu_actions(self):
        """Conecta ações do menu às funções correspondentes."""
        # Menu Arquivo
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(self.closeEvent)
        self.actionHide.triggered.connect(self.hide)

        # Menu Exibir
        self.actionReset_zoom.triggered.connect(
            lambda: self._current_page().set_zoom_factor_page()
        )
        self.actionToggle_full_screen.triggered.connect(self.toggle_fullscreen)
        self.actionZoom_in.triggered.connect(
            lambda: self._current_page().set_zoom_factor_page(+0.1)
        )
        self.actionZoom_out.triggered.connect(
            lambda: self._current_page().set_zoom_factor_page(-0.1)
        )

    def open_settings(self):
        """Abre o painel de configurações."""
        # Implementação futura
        pass

    def toggle_fullscreen(self):
        """Alterna entre os modos de tela cheia e janela."""
        self.is_fullscreen = not self.is_fullscreen
        self.showFullScreen() if self.is_fullscreen else self.showNormal()

    def closeEvent(self, event):
        """
        Evento chamado ao fechar a janela.
        Salva o estado da janela e realiza a limpeza de recursos.
        """
        # Salvar configurações da janela
        SettingsManager.set("main/geometry", self.saveGeometry())
        SettingsManager.set("main/windowState", self.saveState())

        # Esconder em vez de fechar, se configurado
        if SettingsManager.get("system/keep_background", True) and event:
            self.hide()
            event.ignore()
        else:
            self.browser.__del__()
            QApplication.instance().quit()

    def show_window(self):
        """Alterna a visibilidade da janela principal baseada no estado atual."""
        if self.isHidden():
            # Se a janela estiver escondida, mostre-a
            self.showNormal()
            QApplication.instance().setActiveWindow(self)
        elif not self.isActiveWindow():
            # Se estiver visível, mas não estiver em foco, traga para o foco
            self.activateWindow()
            self.raise_()
        else:
            # Se já estiver em foco, esconda
            self.hide()

    def _current_page(self):
        """Retorna a página atual do navegador."""
        return self.browser.pages.currentWidget()
