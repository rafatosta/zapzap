from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
from zapzap.controllers.Browser import Browser
from zapzap.services.SysTray import SysTray


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

        self.init_ui()
        self.init_menu_actions()

    def init_ui(self):
        """Inicializa os elementos principais da interface."""
        SysTray.show()  # Exibe o SysTray
        self.setCentralWidget(self.browser)  # Define o widget central como o navegador

    def init_menu_actions(self):
        """Conecta ações do menu às funções correspondentes."""
        # Menu Arquivo
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(self.close)
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
        Realiza a limpeza de recursos antes de encerrar.
        """
        print("Encerrando o aplicativo...")
        self.browser.__del__()
        super().closeEvent(event)

    def _current_page(self):
        """Retorna a página atual do navegador."""
        return self.browser.pages.currentWidget()
