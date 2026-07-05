from PyQt6.QtWidgets import QVBoxLayout, QWidget, QStyle

from zapzap.models.settings.general_settings_model import GeneralSettingsModel
from zapzap.views.pages.settings import GeneralSettingsView
from zapzap.features.downloads.DownloadManager import DownloadManager
from gettext import gettext as _


class GeneralSettingsController(QWidget):
    """Gerencia a página de configurações gerais de aparência e idioma."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = GeneralSettingsModel()

        self._setup_ui()
        self._initialize()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = GeneralSettingsView(self)
        layout.addWidget(self.view)

    def _initialize(self):
        """Load saved settings and connect view signals."""
        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        self.view.start_background.checkbox.setChecked(
            self.model.start_in_background)
        self.view.start_system.checkbox.setChecked(
            self.model.start_with_system)

    def _configure_signals(self):
        self.view.start_background.checkbox.toggled.connect(
            self._handle_toggle_start_background
        )
        self.view.start_system.checkbox.toggled.connect(
            self._handle_toggle_start_system
        )

    def _handle_toggle_start_background(self, is_enabled: bool):
        self.model.start_in_background = is_enabled

    def _handle_toggle_start_system(self, is_enabled: bool):
        self.model.start_with_system = is_enabled
