from PyQt6.QtWidgets import QWidget, QApplication, QLineEdit
from zapzap.controllers.PageGeneral import PageGeneral
from zapzap.controllers.PageAbout import PageAbout
from zapzap.controllers.PageNetwork import PageNetwork
from zapzap.controllers.PageNotifications import PageNotifications
from zapzap.controllers.PageAccount import PageAccount
from zapzap.controllers.PageAppearance import PageAppearance
from zapzap.controllers.PageCustomizations import PageCustomizations
from zapzap.controllers.PagePerformance import PagePerformance
from zapzap.views.ui_settings import Ui_Settings
from gettext import gettext as _


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
        self._setup_search()

        self._add_page(PageGeneral(), self.btn_page_general)
        self._add_page(PageAccount(), self.btn_account)
        self._add_page(PageAppearance(), self.btn_page_appearence)
        self._add_page(PageCustomizations(), self.btn_page_customizations)
        self._add_page(PageNotifications(), self.btn_page_notifications)
        self._add_page(PageNetwork(), self.btn_page_network)
        self._add_page(PagePerformance(), self.btn_page_performance)
        self._add_page(PageAbout(), self.btn_page_help)

        self._button_search_terms = {
            self.btn_page_general: "general downloads spellchecker behavior wayland",
            self.btn_account: "accounts profile multi account",
            self.btn_page_appearence: "appearance theme dark light scale",
            self.btn_page_customizations: "customizations css js script style",
            self.btn_page_notifications: "notifications tray alert sound",
            self.btn_page_network: "network proxy connection internet",
            self.btn_page_performance: "performance cache hardware acceleration",
            self.btn_page_help: "about help support version",
        }

    def _setup_search(self):
        """Adiciona busca rápida de páginas para melhorar descoberta das configurações."""
        self.input_search = QLineEdit(self.menu_layout)
        self.input_search.setClearButtonEnabled(True)
        self.input_search.setPlaceholderText(_("Search settings..."))
        self.verticalLayout_2.insertWidget(1, self.input_search)

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        self.btn_quit.clicked.connect(
            QApplication.instance().getWindow().closeEvent)
        self.btn_back.clicked.connect(
            QApplication.instance().getWindow().close_settings)
        self.input_search.textChanged.connect(self._filter_pages)

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

    def _filter_pages(self, text: str):
        """Filtra os botões das páginas com base na busca do usuário."""
        query = text.strip().lower()
        visible_buttons = []

        for button in self.page_buttons.values():
            search_blob = f"{button.text().lower()} {self._button_search_terms.get(button, '')}"
            is_visible = not query or query in search_blob
            button.setVisible(is_visible)
            if is_visible:
                visible_buttons.append(button)

        # Mantém o fluxo: se página atual ficou invisível, seleciona a primeira visível
        current_button = self.page_buttons.get(self.pages.currentIndex())
        if current_button and not current_button.isVisible() and visible_buttons:
            visible_buttons[0].click()

    def open_about(self):
        """Abre a página Ajuda"""
        self.btn_page_help.click()
