"""Controller for the permissions settings page."""

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.pages.permissions.model import PermissionsSettingsModel
from zapzap.features.settings.pages.permissions.view import PermissionsSettingsView


class PermissionsSettingsController(PermissionsSettingsView):
    """Coordinates WebEngine permission settings persistence."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = PermissionsSettingsModel()
        self._initialize()

    def _initialize(self):
        self._configure_ui()
        self._load_settings()
        self._connect_signals()

    def _configure_ui(self):
        self.configure_flatpak(self.model.is_flatpak())

    def _load_settings(self):
        for permission_id, row in self.permission_rows.items():
            row.checkbox.setChecked(self.model.is_enabled(permission_id))

        self.flatpak_command_input.setText(self.model.FLATPAK_OVERRIDE_COMMAND)

    def _connect_signals(self):
        self.btn_copy_flatpak_command.clicked.connect(
            lambda: QApplication.clipboard().setText(
                self.model.FLATPAK_OVERRIDE_COMMAND
            )
        )
        self.btn_open_flatseal.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
            )
        )

        for permission_id, row in self.permission_rows.items():
            row.checkbox.toggled.connect(
                lambda enabled, current_permission_id=permission_id: self.model.set_enabled(
                    current_permission_id,
                    enabled,
                )
            )
