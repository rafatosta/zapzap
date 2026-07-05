"""Controller for the permissions settings page."""

from zapzap.features.settings.pages.permissions.model import PermissionsSettingsModel
from zapzap.features.settings.pages.permissions.view import PermissionsSettingsView


class PermissionsSettingsController(PermissionsSettingsView):
    """Coordinates WebEngine permission settings persistence."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = PermissionsSettingsModel()
        self._initialize()

    def _initialize(self):
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        for permission_id, row in self.permission_rows.items():
            row.checkbox.setChecked(self.model.is_enabled(permission_id))

    def _connect_signals(self):
        for permission_id, row in self.permission_rows.items():
            row.checkbox.toggled.connect(
                lambda enabled, current_permission_id=permission_id: self.model.set_enabled(
                    current_permission_id,
                    enabled,
                )
            )
