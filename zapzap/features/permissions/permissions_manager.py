"""Persistence helpers for WebEngine feature permissions."""

from __future__ import annotations

from zapzap.core.config.settings_manager import SettingsManager


class PermissionsManager:
    """Centralizes user preferences for automatic WebEngine permissions."""

    PERMISSIONS = (
        ("MediaAudioCapture", "microphone"),
        ("MediaVideoCapture", "camera"),
        ("MediaAudioVideoCapture", "camera_microphone"),
        ("Geolocation", "location"),
        ("DesktopVideoCapture", "screen_contents"),
        ("DesktopAudioVideoCapture", "screen_contents_audio"),
        ("MouseLock", "mouse_lock"),
    )

    _KEY_PREFIX = "permissions/auto_grant"

    @classmethod
    def key_for(cls, permission_id: str) -> str:
        return f"{cls._KEY_PREFIX}/{permission_id}"

    @classmethod
    def feature_key(cls, feature) -> str | None:
        """Resolve WebEngine enum values only on the real browser path."""
        from PyQt6.QtWebEngineCore import QWebEnginePage

        for feature_name, permission_id in cls.PERMISSIONS:
            if feature == getattr(QWebEnginePage.Feature, feature_name):
                return cls.key_for(permission_id)
        return None

    @classmethod
    def is_auto_grant_enabled(cls, feature) -> bool:
        key = cls.feature_key(feature)
        if key is None:
            return False
        return bool(SettingsManager.get(key, False))

    @classmethod
    def get_auto_grant(cls, permission_id: str) -> bool:
        return bool(SettingsManager.get(cls.key_for(permission_id), False))

    @classmethod
    def set_auto_grant(cls, permission_id: str, enabled: bool) -> None:
        SettingsManager.set(cls.key_for(permission_id), bool(enabled))
