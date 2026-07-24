"""Controller for the permissions settings page."""

from functools import partial

from PyQt6.QtCore import QSignalBlocker, QUrl
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
        self._update_global_permission_actions()

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
        self.btn_allow_all.clicked.connect(
            lambda: self._set_all_permissions(True)
        )
        self.btn_remove_all.clicked.connect(
            lambda: self._set_all_permissions(False)
        )

        for permission_id, row in self.permission_rows.items():
            row.checkbox.toggled.connect(
                partial(self._on_permission_toggled, permission_id)
            )

    def _on_permission_toggled(self, permission_id: str, enabled: bool) -> None:
        self._persist_permission_state(permission_id, enabled)
        self._update_global_permission_actions()

    def _persist_permission_state(
        self,
        permission_id: str,
        enabled: bool,
    ) -> None:
        self.model.set_enabled(permission_id, enabled)

    def _set_all_permissions(self, enabled: bool) -> None:
        for permission_id, row in self.permission_rows.items():
            checkbox = row.checkbox
            if checkbox.isChecked() == enabled:
                continue

            blocker = QSignalBlocker(checkbox)
            checkbox.setChecked(enabled)
            self._persist_permission_state(permission_id, enabled)
            del blocker

        self._update_global_permission_actions()

    def _update_global_permission_actions(self) -> None:
        states = [
            row.checkbox.isChecked()
            for row in self.permission_rows.values()
        ]
        self.btn_allow_all.setEnabled(not all(states))
        self.btn_remove_all.setEnabled(any(states))
