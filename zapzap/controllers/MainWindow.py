from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QByteArray
from zapzap.controllers.Settings import Settings
from zapzap.controllers.Browser import Browser
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager


class MainWindow(QMainWindow):
    """
    Classe principal da interface do aplicativo.
    Controla a janela principal, incluindo o menu e interações com widgets centrais.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_mainwindow.ui", self)

        self.is_fullscreen = False  # Controle do estado de tela cheia
        self.browser = Browser()  # Inicialização do navegador
        self.app_settings = None

        self._setup_ui()

    # === Configuração Inicial ===
    def _setup_ui(self):
        """Configurações iniciais da interface e conexões de menu."""
        self.stackedWidget.addWidget(self.browser)
        self._connect_menu_actions()

    def load_settings(self):
        """Restaura as configurações salvas da janela e do sistema."""
        self.restoreGeometry(SettingsManager.get(
            "main/geometry", QByteArray()))
        self.restoreState(SettingsManager.get(
            "main/windowState", QByteArray()))

        # Exibe o SysTray e inicia o ThemeManager
        SysTrayManager.show()
        ThemeManager.start()

    # === Conexões de Ações do Menu ===
    def _connect_menu_actions(self):
        """Conecta ações do menu às funções correspondentes."""
        self._connect_file_menu_actions()
        self._connect_view_menu_actions()

    def _connect_file_menu_actions(self):
        """Conectar ações do menu 'Arquivo'."""
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(self.closeEvent)
        self.actionHide.triggered.connect(self.hide)
        self.actionReload.triggered.connect(self.browser.reload_pages)
        self.actionNew_chat.triggered.connect(self._new_chat)
        self.actionBy_phone_number.triggered.connect(self._new_chat_by_phone)

    def _connect_view_menu_actions(self):
        """Conectar ações do menu 'Exibir'."""
        self.actionReset_zoom.triggered.connect(self._reset_zoom)
        self.actionToggle_full_screen.triggered.connect(self.toggle_fullscreen)
        self.actionZoom_in.triggered.connect(self._zoom_in)
        self.actionZoom_out.triggered.connect(self._zoom_out)

    # === Ações de Menu ===
    def _new_chat(self):
        """Iniciar um novo chat na página atual."""
        self._current_page().page().new_chat()

    def _new_chat_by_phone(self):
        """Iniciar um novo chat pelo número de telefone na página atual."""
        self._current_page().page().open_chat_by_number()

    def _reset_zoom(self):
        """Resetar o fator de zoom da página atual."""
        self._current_page().set_zoom_factor_page()

    def _zoom_in(self):
        """Aumentar o zoom da página atual."""
        self._current_page().set_zoom_factor_page(+0.1)

    def _zoom_out(self):
        """Diminuir o zoom da página atual."""
        self._current_page().set_zoom_factor_page(-0.1)

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
        self._save_window_state()

        if self._should_keep_background(event):
            self._prepare_for_background(event)
        else:
            self._clean_up_and_exit()

    def _save_window_state(self):
        """Salvar a geometria e o estado da janela."""
        SettingsManager.set("main/geometry", self.saveGeometry())
        SettingsManager.set("main/windowState", self.saveState())

    def _should_keep_background(self, event) -> bool:
        """Verificar se o app deve continuar em segundo plano."""
        return SettingsManager.get("system/keep_background", True) and event

    def _prepare_for_background(self, event):
        """Preparar o app para permanecer em segundo plano."""
        self.browser.close_conversations()
        self.hide()
        event.ignore()

    def _clean_up_and_exit(self):
        """Limpar recursos e sair do aplicativo."""
        self.browser.__del__()
        QApplication.instance().quit()

    # === Controle de Visibilidade da Janela ===
    def show_window(self):
        """Alterna a visibilidade da janela principal."""
        if self.isHidden():
            self.showNormal()
            QApplication.instance().setActiveWindow(self)
        elif not self.isActiveWindow():
            self.activateWindow()
            self.raise_()
        else:
            self.hide()

    # === Funções de Configuração ===
    def open_settings(self):
        """Abre o painel de configurações."""
        self.app_settings = Settings()
        self.stackedWidget.addWidget(self.app_settings)
        self.stackedWidget.setCurrentWidget(self.app_settings)

    def close_settings(self):
        """Fecha o painel de configurações."""
        self.stackedWidget.removeWidget(self.app_settings)
        self.app_settings.__del__()

        self.stackedWidget.setCurrentWidget(self.browser)

    # === Eventos externos ===
    def xdgOpenChat(self, url):
        """Open chat by clicking on a notification"""
        self._current_page.page().xdg_open_chat(url)
