"""Controller for the settings shell."""

from dataclasses import dataclass
from gettext import gettext as _
from importlib import import_module

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from zapzap import __donationPage__
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.settings.shell.settings_view import SettingsView


@dataclass(frozen=True)
class SettingsPageDescriptor:
    """Stable navigation metadata and a lazy controller factory."""

    page_id: str
    label: str
    module_name: str
    controller_name: str

    def create(self):
        module = import_module(self.module_name)
        controller = getattr(module, self.controller_name)
        return controller()

    def matches_type(self, page_type):
        return (
            page_type.__module__ == self.module_name
            and page_type.__name__ == self.controller_name
        )


class SettingsController(SettingsView):
    """Coordinates lazy settings navigation and shell actions."""

    DEFAULT_PAGE_ID = "accounts"
    LANGUAGE_DOWNLOADS_PAGE_ID = "language_downloads"
    ABOUT_PAGE_ID = "about"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_buttons = {}
        self._page_descriptors = {}
        self._page_instances = {}
        self._current_page_id = None
        self._register_pages()
        self._setup_signals()
        self._select_default_page()

    def __del__(self):
        """Destrói o widget e limpa recursos."""

    def _pages(self):
        """Return page descriptors with labels translated at runtime."""
        return [
            SettingsPageDescriptor(
                "accounts",
                _("Accounts"),
                "zapzap.features.settings.pages.accounts.controller",
                "AccountsSettingsController",
            ),
            SettingsPageDescriptor(
                "appearance",
                _("Appearance"),
                "zapzap.features.settings.pages.appearance.controller",
                "AppearanceSettingsController",
            ),
            SettingsPageDescriptor(
                "notifications",
                _("Notifications"),
                "zapzap.features.settings.pages.notifications.controller",
                "NotificationsSettingsController",
            ),
            SettingsPageDescriptor(
                "permissions",
                _("Permissions"),
                "zapzap.features.settings.pages.permissions.controller",
                "PermissionsSettingsController",
            ),
            SettingsPageDescriptor(
                "system_startup",
                _("System and startup"),
                "zapzap.features.settings.pages.system_startup.controller",
                "SystemStartupSettingsController",
            ),
            SettingsPageDescriptor(
                self.LANGUAGE_DOWNLOADS_PAGE_ID,
                _("Language and Download"),
                "zapzap.features.settings.pages.language_downloads.controller",
                "LanguageDownloadSettingsController",
            ),
            SettingsPageDescriptor(
                "network_privacy",
                _("Privacy and Network"),
                "zapzap.features.settings.pages.network_privacy.controller",
                "NetworkPrivacySettingsController",
            ),
            SettingsPageDescriptor(
                "advanced_customizations",
                _("Advanced Customizations"),
                "zapzap.features.settings.pages.advanced_customizations.controller",
                "AdvancedCustomizationsSettingsController",
            ),
            SettingsPageDescriptor(
                "performance_experimental",
                _("Performance experimental"),
                "zapzap.features.settings.pages.performance_experimental.controller",
                "PerformanceExperimentalSettingsController",
            ),
            SettingsPageDescriptor(
                "debugging",
                _("Debugging"),
                "zapzap.features.settings.pages.debugging.controller",
                "DebuggingSettingsController",
            ),
            SettingsPageDescriptor(
                self.ABOUT_PAGE_ID,
                _("About"),
                "zapzap.features.settings.pages.about.controller",
                "AboutSettingsController",
            ),
        ]

    def _register_pages(self):
        for descriptor in self._pages():
            if descriptor.page_id in self._page_descriptors:
                raise ValueError(f"Duplicate settings page ID: {descriptor.page_id}")
            self._page_descriptors[descriptor.page_id] = descriptor
            button = self.add_navigation_item(descriptor.label)
            self.page_buttons[descriptor.page_id] = button
            button.clicked.connect(
                lambda _checked=False, page_id=descriptor.page_id: (
                    self.open_page_id(page_id)
                )
            )
        self.finish_sidebar()

    def _setup_signals(self):
        """Conecta os sinais dos botões gerais."""
        window = QApplication.instance().getWindow()
        self.btn_quit.clicked.connect(window.request_quit)
        self.sidebar.btn_close.clicked.connect(window.close_settings)
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(
            Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        self.close_shortcut.activated.connect(window.close_settings)
        self.btn_donate.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__))
        )

    def _ensure_page(self, page_id):
        page = self._page_instances.get(page_id)
        if page is not None:
            return page

        descriptor = self._page_descriptors.get(page_id)
        if descriptor is None:
            return None

        try:
            page = descriptor.create()
            if not isinstance(page, QWidget):
                raise TypeError(descriptor.controller_name)
        except Exception as error:
            AlertManager.critical(
                self,
                _("Settings"),
                f"{descriptor.label}\n\n{error}",
            )
            return None

        self.add_page(page)
        self._page_instances[page_id] = page
        return page

    def open_page_id(self, page_id):
        """Create a registered page on first use and select it."""
        page = self._ensure_page(page_id)
        if page is None:
            return None
        return self.switch_to_page(page)

    def switch_to_page(self, page: QWidget):
        """Select an instantiated page without recreating it."""
        page_id = next(
            (
                registered_id
                for registered_id, instance in self._page_instances.items()
                if instance is page
            ),
            None,
        )
        if page_id is None:
            return None

        self._reset_button_styles()
        self.set_current_page(page)
        self.page_buttons[page_id].setEnabled(False)
        self._current_page_id = page_id
        return page

    def _reset_button_styles(self):
        """Reativa todos os botões."""
        for button in self.page_buttons.values():
            button.setEnabled(True)

    def _select_default_page(self):
        """Create and select only the default page."""
        self.open_page_id(self.DEFAULT_PAGE_ID)

    @property
    def current_page_id(self):
        return self._current_page_id

    def page_instance(self, page_id):
        """Return an already-created page without triggering construction."""
        return self._page_instances.get(page_id)

    def open_about(self):
        """Abre a página Ajuda."""
        return self.open_page_id(self.ABOUT_PAGE_ID)

    def open_page_type(self, page_type):
        """Create and select a registered page by its public controller type."""
        for page_id, page in self._page_instances.items():
            if isinstance(page, page_type):
                return self.open_page_id(page_id)

        for page_id, descriptor in self._page_descriptors.items():
            if descriptor.matches_type(page_type):
                return self.open_page_id(page_id)
        return None

    def open_language_downloads(self):
        page = self.open_page_id(self.LANGUAGE_DOWNLOADS_PAGE_ID)
        if page is not None:
            page.focus_spellchecker_management()
        return page
