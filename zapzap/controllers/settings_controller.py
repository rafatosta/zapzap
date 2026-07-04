"""Controller for the settings shell."""

from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QWidget

from zapzap import __donationPage__

from zapzap.controllers.settings.appearance_settings_controller import AppearanceSettingsController
from zapzap.controllers.settings.language_downloads_settings_controller import LanguageDownloadSettingsController
from zapzap.controllers.settings.notifications_settings_controller import NotificationsSettingsController
from zapzap.controllers.settings.system_startup_settings_controller import SystemStartupSettingsController
from zapzap.views import SettingsView


class SettingsController(SettingsView):
    """Coordinates settings navigation and shell actions."""

    # Exemplo: (PageGeneral, _("General"))
    _PAGES = [
        (QWidget, _("Contas")),
        (AppearanceSettingsController, _("Appearance")),
        (NotificationsSettingsController, _("Notifications")),
        (LanguageDownloadSettingsController, _("Idioma e downloads")),
        (QWidget, _("Privacidade e rede")),
        (QWidget, _("Customizações avançadas")),
        (QWidget, _("Performance experimental")),
        (SystemStartupSettingsController, _("Sistema e inicialização")),
        (QWidget, _("Suporte")),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_buttons = {}
        self._register_pages()
        self._setup_signals()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _register_pages(self):
        for page_class, label in self._PAGES:
            self._add_page(
                page_class(),
                self.add_navigation_item(label),
            )
        self.finish_sidebar()

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        window = QApplication.instance().getWindow()
        self.btn_quit.clicked.connect(window.closeEvent)
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
