"""Model for WebEngine permission settings persistence."""

from __future__ import annotations

from zapzap.core.environment.setup_manager import SetupManager
from zapzap.features.permissions.permissions_manager import PermissionsManager


class PermissionsSettingsModel:
    """Exposes automatic permission grant preferences to settings controllers."""

    permissions = PermissionsManager.PERMISSIONS
    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    def is_flatpak(self) -> bool:
        return SetupManager._is_flatpak

    def is_enabled(self, permission_id: str) -> bool:
        return PermissionsManager.get_auto_grant(permission_id)

    def set_enabled(self, permission_id: str, enabled: bool) -> None:
        PermissionsManager.set_auto_grant(permission_id, enabled)
