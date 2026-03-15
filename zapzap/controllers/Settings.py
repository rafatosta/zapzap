from gettext import gettext as _

from PyQt6.QtWidgets import QWidget, QApplication, QLineEdit
from PyQt6.QtCore import QTimer
from zapzap.controllers.PageGeneral import PageGeneral
from zapzap.controllers.PageAbout import PageAbout
from zapzap.controllers.PageNetwork import PageNetwork
from zapzap.controllers.PageNotifications import PageNotifications
from zapzap.controllers.PageAccount import PageAccount
from zapzap.controllers.PageAppearance import PageAppearance
from zapzap.controllers.PageCustomizations import PageCustomizations
from zapzap.controllers.PagePerformance import PagePerformance
from zapzap.views.ui_settings import Ui_Settings
from zapzap.ui.search_settings import SETTINGS_INDEX


class Settings(QWidget, Ui_Settings):
    # Maps the page keys used in SETTINGS_INDEX to nav buttons
    _PAGE_KEY_TO_BUTTON = {
        "general": "btn_page_general",
        "account": "btn_account",
        "appearance": "btn_page_appearence",
        "customizations": "btn_page_customizations",
        "notifications": "btn_page_notifications",
        "network": "btn_page_network",
        "performance": "btn_page_performance",
        "about": "btn_page_help",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.page_buttons = {}  # Mapear botões às páginas
        self._page_key_to_widget = {}  # page_key → QWidget page
        self._search_debounce = QTimer(self)
        self._search_debounce.setSingleShot(True)
        self._search_debounce.timeout.connect(self._apply_search)

        self._setup_ui()
        self._setup_search()
        self._setup_signals()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _setup_ui(self):
        """Configura as páginas e associa os botões às páginas."""
        pages = [
            ("general", PageGeneral(), self.btn_page_general),
            ("account", PageAccount(), self.btn_account),
            ("appearance", PageAppearance(), self.btn_page_appearence),
            ("customizations", PageCustomizations(), self.btn_page_customizations),
            ("notifications", PageNotifications(), self.btn_page_notifications),
            ("network", PageNetwork(), self.btn_page_network),
            ("performance", PagePerformance(), self.btn_page_performance),
            ("about", PageAbout(), self.btn_page_help),
        ]
        for key, page, button in pages:
            self._add_page(page, button)
            self._page_key_to_widget[key] = page

    def _setup_search(self):
        """Adiciona barra de busca ao topo da barra lateral."""
        self._search_input = QLineEdit(self)
        self._search_input.setPlaceholderText(_("Search settings…"))
        self._search_input.setClearButtonEnabled(True)
        self._search_input.setObjectName("settings_search_input")
        self._search_input.textChanged.connect(
            lambda: self._search_debounce.start(200)
        )
        # Insert just below the Back button (position 1)
        self.verticalLayout_2.insertWidget(1, self._search_input)

    def _apply_search(self):
        """Filtra os botões de navegação com base no texto de busca."""
        query = self._search_input.text().strip().lower()

        if not query:
            # Restore all navigation buttons to visible
            for button in self.page_buttons.values():
                button.setVisible(True)
            return

        # Find which page keys match the query
        matching_keys = set()
        for entry in SETTINGS_INDEX:
            if any(query in kw for kw in entry["keywords"]):
                matching_keys.add(entry["page"])

        # Show only buttons for matching pages; navigate to first match
        first_match = None
        for key, page in self._page_key_to_widget.items():
            btn_name = self._PAGE_KEY_TO_BUTTON.get(key)
            if btn_name:
                button = getattr(self, btn_name, None)
                if button:
                    visible = key in matching_keys
                    button.setVisible(visible)
                    if visible and first_match is None:
                        first_match = page

        if first_match:
            self.switch_to_page(first_match)

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

    def open_about(self):
        """Abre a página Ajuda"""
        self.btn_page_help.click()

