"""Controller for the settings shell."""

from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from zapzap import __donationPage__
from zapzap.controllers.PageAbout import PageAbout
from zapzap.controllers.PageAccount import PageAccount
from zapzap.controllers.PageAppearance import PageAppearance
from zapzap.controllers.PageCustomizations import PageCustomizations
from zapzap.controllers.PageDebugging import PageDebugging
from zapzap.controllers.PageGeneral import PageGeneral
from zapzap.controllers.PageNetwork import PageNetwork
from zapzap.controllers.PageNotifications import PageNotifications
from zapzap.controllers.PagePerformance import PagePerformance
from zapzap.views.pages.settings_view import SettingsView


class SettingsController(QWidget):
    """Coordinates settings navigation and shell actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_buttons = {}
        self.view = SettingsView(self)
        self._setup_ui()
        self._register_pages()
        self._setup_signals()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.sidebar = self.view.sidebar
        self.pages = self.view.pages
        self.btn_donate = self.view.btn_donate
        self.btn_back = self.view.btn_back
        self.btn_quit = self.view.btn_quit

    def _register_pages(self):
        self._add_page(PageGeneral(), self.view.add_navigation_item(_("General")))
        self._add_page(PageAccount(), self.view.add_navigation_item(_("Accounts")))
        self._add_page(PageAppearance(), self.view.add_navigation_item(_("Appearance")))
        self._add_page(
            PageCustomizations(),
            self.view.add_navigation_item(_("Customizations")),
        )
        self._add_page(
            PageNotifications(),
            self.view.add_navigation_item(_("Notifications")),
        )
        self._add_page(PageNetwork(), self.view.add_navigation_item(_("Network")))
        self._add_page(
            PagePerformance(),
            self.view.add_navigation_item(_("Performance")),
        )
        self._add_page(PageDebugging(), self.view.add_navigation_item(_("Debugging")))
        self._add_page(PageAbout(), self.view.add_navigation_item(_("About")))
        self.view.finish_sidebar()

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        window = QApplication.instance().getWindow()
        self.btn_quit.clicked.connect(window.closeEvent)
        self.btn_back.clicked.connect(window.close_settings)
        self.btn_donate.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__))
        )

    def _add_page(self, page: QWidget, button):
        """Adiciona uma página ao widget de páginas e associa ao botão."""
        page_index = self.view.add_page(page)
        self.page_buttons[page_index] = button
        button.clicked.connect(lambda: self.switch_to_page(page))

    def switch_to_page(self, page: QWidget):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        self._reset_button_styles()
        self.view.set_current_page(page)
        self.page_buttons[self.view.page_index(page)].setEnabled(False)

    def _reset_button_styles(self):
        """Reativa todos os botões."""
        for button in self.page_buttons.values():
            button.setEnabled(True)

    def _select_default_page(self):
        """Seleciona a primeira página como padrão."""
        if self.page_buttons:
            self.switch_to_page(self.view.page_at(0))

    def open_about(self):
        """Abre a página Ajuda"""
        self.switch_to_page(self.view.page_at(8))
