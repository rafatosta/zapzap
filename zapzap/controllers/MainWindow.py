from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QByteArray

from zapzap.controllers.Browser import Browser
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager


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

        self._setup_ui()

    # === Configuração Inicial ===
    def _setup_ui(self):
        """Configurações iniciais da interface e conexões de menu."""
        self.setCentralWidget(self.browser)
        self._connect_menu_actions()

    def load_settings(self):
        """Restaura as configurações salvas da janela e do sistema. (Chamar após a criação do objeto)"""
        self.restoreGeometry(SettingsManager.get(
            "main/geometry", QByteArray()))
        self.restoreState(SettingsManager.get(
            "main/windowState", QByteArray()))

        SysTrayManager.show()  # Exibe o SysTray
        ThemeManager.start()  # Iniciar o ThemeManager

    # === Conexões de Ações do Menu ===
    def _connect_menu_actions(self):
        """Conecta ações do menu às funções correspondentes."""
        # Menu Arquivo
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(self.closeEvent)
        self.actionHide.triggered.connect(self.hide)
        self.actionReload.triggered.connect(self.browser.reload_pages)
        self.actionNew_chat.triggered.connect(
            lambda: self._current_page().new_chat())
        self.actionBy_phone_number.triggered.connect(
            lambda: self._current_page().new_chat_by_phone())

        # Menu Exibir
        self.actionReset_zoom.triggered.connect(
            lambda: self._current_page().set_zoom_factor_page())
        self.actionToggle_full_screen.triggered.connect(self.toggle_fullscreen)
        self.actionZoom_in.triggered.connect(
            lambda: self._current_page().set_zoom_factor_page(+0.1))
        self.actionZoom_out.triggered.connect(
            lambda: self._current_page().set_zoom_factor_page(-0.1))

    # === Gerenciamento de Tela ===
    def _current_page(self):
        """Retorna a página atual do navegador."""
        return self.browser.pages.currentWidget()

    def toggle_fullscreen(self):
        """Alterna entre os modos de tela cheia e janela."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()

    # === Configurações de Fechamento ===
    def closeEvent(self, event):
        """
        Evento chamado ao fechar a janela.
        Salva o estado da janela e realiza a limpeza de recursos.
        """
        # Salva a geometria e o estado da janela
        SettingsManager.set("main/geometry", self.saveGeometry())
        SettingsManager.set("main/windowState", self.saveState())

        # Verifica se deve manter o app em segundo plano ou fechar completamente
        if SettingsManager.get("system/keep_background", True) and event:
            self.browser.close_conversations()
            self.hide()
            event.ignore()
        else:
            self.browser.__del__()  # Limpeza do navegador
            QApplication.instance().quit()

    # === Controle de Visibilidade da Janela ===
    def show_window(self):
        """Alterna a visibilidade da janela principal."""
        if self.isHidden():
            # Se a janela estiver escondida, mostra-a
            self.showNormal()
            QApplication.instance().setActiveWindow(self)
        elif not self.isActiveWindow():
            # Se estiver visível, mas não em foco, traz para o foco
            self.activateWindow()
            self.raise_()
        else:
            # Se já estiver em foco, esconde
            self.hide()

    # === Funções de Configuração Futura ===
    def open_settings(self):
        """Abre o painel de configurações."""
        # Implementação futura
        pass
