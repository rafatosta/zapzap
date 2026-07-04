"""Model for network and privacy settings persistence."""

from __future__ import annotations

from zapzap.models.User import User
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager


class NetworkPrivacySettingsModel:
    """Model for proxy and network privacy settings.

    This class hides SettingsManager keys from controllers and views.
    Controllers should access network settings through semantic methods such as
    `load_proxy_settings`, `save_proxy_settings`, and `webrtc_shield_enabled`.
    """

    _GLOBAL_PROXY_PREFIX = "proxy/"
    _WEBRTC_SHIELD = ("privacy/webrtc_shield", False)

    def list_scopes(self) -> list[tuple[str, int | None]]:
        """Return available proxy scopes as `(label, user_id)` pairs."""
        scopes: list[tuple[str, int | None]] = [("Global (Default)", None)]
        for user in User.select():
            scopes.append((user.name or f"Account {user.id}", user.id))
        return scopes

    def proxy_types(self) -> list[str]:
        """Return available proxy type keys."""
        return list(ProxyManager.PROXY_TYPES.keys())

    def proxy_description(self, proxy_type: str) -> str:
        """Return a human-readable description for a proxy type."""
        return ProxyManager.get_proxy_description(proxy_type)

    def _proxy_prefix(self, user_id: int | None = None) -> str:
        return f"{user_id}/proxy/" if user_id else self._GLOBAL_PROXY_PREFIX

    def load_proxy_settings(self, user_id: int | None = None) -> dict[str, str | bool]:
        """Load proxy settings for a global or per-account scope."""
        prefix = self._proxy_prefix(user_id)
        return {
            "enabled": bool(SettingsManager.get(f"{prefix}proxyEnable", False)),
            "proxy_type": str(SettingsManager.get(f"{prefix}proxyType", "NoProxy")),
            "host": str(SettingsManager.get(f"{prefix}hostName", "")),
            "port": str(SettingsManager.get(f"{prefix}port", "")),
            "user": str(SettingsManager.get(f"{prefix}user", "")),
            "password": str(SettingsManager.get(f"{prefix}password", "")),
        }

    def save_proxy_settings(
        self,
        user_id: int | None,
        *,
        enabled: bool,
        proxy_type: str,
        host: str,
        port: str,
        user: str,
        password: str,
    ) -> None:
        """Persist proxy settings for a global or per-account scope."""
        prefix = self._proxy_prefix(user_id)
        SettingsManager.set(f"{prefix}proxyEnable", bool(enabled))
        SettingsManager.set(f"{prefix}proxyType", str(proxy_type))
        SettingsManager.set(f"{prefix}hostName", str(host))
        SettingsManager.set(f"{prefix}port", str(port))
        SettingsManager.set(f"{prefix}user", str(user))
        SettingsManager.set(f"{prefix}password", str(password))

    def restore_proxy_settings(self, user_id: int | None = None) -> None:
        """Reset proxy settings for a global or per-account scope."""
        self.save_proxy_settings(
            user_id,
            enabled=False,
            proxy_type="NoProxy",
            host="",
            port="",
            user="",
            password="",
        )

    @property
    def webrtc_shield_enabled(self) -> bool:
        """Whether WebRTC IP exposure protection is enabled."""
        key, default = self._WEBRTC_SHIELD
        return bool(SettingsManager.get(key, default))

    @webrtc_shield_enabled.setter
    def webrtc_shield_enabled(self, value: bool) -> None:
        key, _default = self._WEBRTC_SHIELD
        SettingsManager.set(key, bool(value))

    def apply_proxy(self) -> None:
        """Apply the currently persisted proxy configuration."""
        ProxyManager.apply()
