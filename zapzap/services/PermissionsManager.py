"""Persistence helpers for WebEngine feature permissions."""

from __future__ import annotations

from PyQt6.QtWebEngineCore import QWebEnginePage

from zapzap.services.SettingsManager import SettingsManager


class PermissionsManager:
    """Centralizes user preferences for automatic WebEngine permissions."""

    Feature = QWebEnginePage.Feature

    PERMISSIONS = (
        (Feature.MediaAudioCapture, "microphone"),
        (Feature.MediaVideoCapture, "camera"),
        (Feature.MediaAudioVideoCapture, "camera_microphone"),
        (Feature.Geolocation, "location"),
        (Feature.DesktopVideoCapture, "screen_contents"),
        (Feature.DesktopAudioVideoCapture, "screen_contents_audio"),
        (Feature.MouseLock, "mouse_lock"),
    )

    _KEY_PREFIX = "permissions/auto_grant"

    @classmethod
    def key_for(cls, permission_id: str) -> str:
        return f"{cls._KEY_PREFIX}/{permission_id}"

    @classmethod
    def feature_key(cls, feature: QWebEnginePage.Feature) -> str | None:
        for item_feature, permission_id in cls.PERMISSIONS:
            if feature == item_feature:
                return cls.key_for(permission_id)
        return None

    @classmethod
    def is_auto_grant_enabled(cls, feature: QWebEnginePage.Feature) -> bool:
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
