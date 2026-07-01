from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout, QWidget

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
from zapzap.views.settings_components import SettingsSidebar, apply_settings_style


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsRoot")
        self.page_buttons = {}

        self._setup_ui()
        self._setup_signals()
        self._select_default_page()
        apply_settings_style(self)

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _setup_ui(self):
        """Build the settings shell and register pages in navigation order."""
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = SettingsSidebar(self)
        self.pages = QStackedWidget(self)
        root.addWidget(self.sidebar)
        root.addWidget(self.pages, 1)

        self._add_page(PageGeneral(), self.sidebar.add_item(_("General")))
        self._add_page(PageAccount(), self.sidebar.add_item(_("Accounts")))
        self._add_page(PageAppearance(), self.sidebar.add_item(_("Appearance")))
        self._add_page(PageCustomizations(), self.sidebar.add_item(_("Customizations")))
        self._add_page(PageNotifications(), self.sidebar.add_item(_("Notifications")))
        self._add_page(PageNetwork(), self.sidebar.add_item(_("Network")))
        self._add_page(PagePerformance(), self.sidebar.add_item(_("Performance")))
        self._add_page(PageDebugging(), self.sidebar.add_item(_("Debugging")))
        self._add_page(PageAbout(), self.sidebar.add_item(_("About")))

        self.sidebar.add_stretch()
        actions = QVBoxLayout()
        actions.setSpacing(8)
        self.btn_donate = QPushButton(_("Donate"))
        self.btn_donate.setObjectName("SettingsDonateButton")
        self.btn_back = QPushButton(_("Back"))
        self.btn_back.setObjectName("SettingsBackButton")
        self.btn_quit = QPushButton(_("Quit"))
        self.btn_quit.setObjectName("SettingsQuitButton")
        actions.addWidget(self.btn_donate)
        actions.addWidget(self.btn_back)
        actions.addWidget(self.btn_quit)
        self.sidebar.layout.addLayout(actions)

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        window = QApplication.instance().getWindow()
        self.btn_quit.clicked.connect(window.closeEvent)
        self.btn_back.clicked.connect(window.close_settings)
        self.btn_donate.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__)))

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
        self.switch_to_page(self.pages.widget(8))
