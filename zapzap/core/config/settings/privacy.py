"""Privacy settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class PrivacySettings(BaseSettings):
    """Semantic access to privacy settings."""

    _WEBRTC_SHIELD = ("privacy/webrtc_shield", False)

    @property
    def webrtc_shield_enabled(self) -> bool:
        return self._get_bool(self._WEBRTC_SHIELD)

    @webrtc_shield_enabled.setter
    def webrtc_shield_enabled(self, value: bool) -> None:
        self._set_bool(self._WEBRTC_SHIELD, value)
