"""Model for WebEngine permission settings persistence."""

from __future__ import annotations

from zapzap.features.permissions.permissions_manager import PermissionsManager


class PermissionsSettingsModel:
    """Exposes automatic permission grant preferences to settings controllers."""

    permissions = PermissionsManager.PERMISSIONS

    def is_enabled(self, permission_id: str) -> bool:
        return PermissionsManager.get_auto_grant(permission_id)

    def set_enabled(self, permission_id: str, enabled: bool) -> None:
        PermissionsManager.set_auto_grant(permission_id, enabled)
