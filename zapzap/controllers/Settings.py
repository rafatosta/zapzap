from PyQt6.QtWidgets import QWidget, QApplication
from zapzap.controllers.PageGeneral import PageGeneral
from zapzap.controllers.PageAbout import PageAbout
from zapzap.controllers.PageNetwork import PageNetwork
from zapzap.controllers.PageNotifications import PageNotifications
from zapzap.controllers.PageAccount import PageAccount
from zapzap.controllers.PageAppearance import PageAppearance
from zapzap.controllers.PagePerformance import PagePerformance
from zapzap.views.ui_settings import Ui_Settings


class Settings(QWidget, Ui_Settings):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.page_buttons = {}  # Mapear botões às páginas

        self._setup_ui()
        self._setup_signals()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _setup_ui(self):
        """Configura as páginas e associa os botões às páginas."""
        self._add_page(PageGeneral(), self.btn_page_general)
        self._add_page(PageAccount(), self.btn_account)
        self._add_page(PageAppearance(), self.btn_page_appearence)
        self._add_page(PageNotifications(), self.btn_page_notifications)
        self._add_page(PageNetwork(), self.btn_page_network)
        self._add_page(PagePerformance(), self.btn_page_performance)
        self._add_page(PageAbout(), self.btn_page_help)

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        self.btn_quit.clicked.connect(
            QApplication.instance().getWindow().closeEvent)
        self.btn_back.clicked.connect(
            QApplication.instance().getWindow().close_settings)

    def _add_page(self, page: QWidget, button):
        """Adiciona uma página ao widget de páginas e associa ao botão."""
        page_index = self.pages.addWidget(page)
        self.page_buttons[page_index] = button
        button.clicked.connect(lambda: self.switch_to_page(page))

    def switch_to_page(self, page: QWidget):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        self._reset_button_styles()
        self.pages.setCurrentWidget(page)
        self.page_buttons[self.pages.indexOf(page)].setEnabled(False)

    def _reset_button_styles(self):
        """Reativa todos os botões."""
        for button in self.page_buttons.values():
            button.setEnabled(True)

    def _select_default_page(self):
        """Seleciona a primeira página como padrão."""
        if self.page_buttons:
            self.switch_to_page(self.pages.widget(0))
