"""Controller for the settings shell."""

from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QWidget

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


class SettingsController(SettingsView):
    """Coordinates settings navigation and shell actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_buttons = {}
        self._register_pages()
        self._setup_signals()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _register_pages(self):
        self._add_page(PageGeneral(), self.add_navigation_item(_("General")))
        self._add_page(PageAccount(), self.add_navigation_item(_("Accounts")))
        self._add_page(PageAppearance(), self.add_navigation_item(_("Appearance")))
        self._add_page(
            PageCustomizations(),
            self.add_navigation_item(_("Customizations")),
        )
        self._add_page(
            PageNotifications(),
            self.add_navigation_item(_("Notifications")),
        )
        self._add_page(PageNetwork(), self.add_navigation_item(_("Network")))
        self._add_page(
            PagePerformance(),
            self.add_navigation_item(_("Performance")),
        )
        self._add_page(PageDebugging(), self.add_navigation_item(_("Debugging")))
        self._add_page(PageAbout(), self.add_navigation_item(_("About")))
        self.finish_sidebar()

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        window = QApplication.instance().getWindow()
        self.btn_quit.clicked.connect(window.closeEvent)
        self.btn_back.clicked.connect(window.close_settings)
        self.sidebar.btn_close.clicked.connect(window.close_settings)
        self.btn_donate.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__))
        )

    def _add_page(self, page: QWidget, button):
        """Adiciona uma página ao widget de páginas e associa ao botão."""
        page_index = self.add_page(page)
        self.page_buttons[page_index] = button
        button.clicked.connect(lambda: self.switch_to_page(page))

    def switch_to_page(self, page: QWidget):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        self._reset_button_styles()
        self.set_current_page(page)
        self.page_buttons[self.page_index(page)].setEnabled(False)

    def _reset_button_styles(self):
        """Reativa todos os botões."""
        for button in self.page_buttons.values():
            button.setEnabled(True)

    def _select_default_page(self):
        """Seleciona a primeira página como padrão."""
        if self.page_buttons:
            self.switch_to_page(self.page_at(0))

    def open_about(self):
        """Abre a página Ajuda"""
        self.switch_to_page(self.page_at(8))
