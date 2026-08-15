"""Model for network and privacy settings persistence."""

from __future__ import annotations

from zapzap.core.environment.proxy_manager import ProxyApplyResult, ProxyManager
from zapzap.core.config.settings.privacy import PrivacySettings
from zapzap.core.config.settings_manager import SettingsManager


class NetworkPrivacySettingsModel:
    """Model for proxy and network privacy settings.

    This class hides SettingsManager keys from controllers and views.
    Controllers should access network settings through semantic methods such as
    `load_proxy_settings`, `save_proxy_settings`, and privacy properties.
    """

    _GLOBAL_PROXY_PREFIX = "proxy/"

    def __init__(self) -> None:
        self._privacy_settings = PrivacySettings()

    def proxy_types(self) -> list[str]:
        """Return available proxy type keys."""
        return list(ProxyManager.PROXY_TYPES.keys())

    def proxy_description(self, proxy_type: str) -> str:
        """Return a human-readable description for a proxy type."""
        return ProxyManager.get_proxy_description(proxy_type)

    def load_proxy_settings(self) -> dict[str, str | bool]:
        """Load the sole application-wide proxy configuration."""
        prefix = self._GLOBAL_PROXY_PREFIX
        return {
            "enabled": bool(SettingsManager.get(f"{prefix}proxyEnable", False)),
            "proxy_type": str(
                SettingsManager.get(f"{prefix}proxyType", "NoProxy")
            ),
            "host": str(SettingsManager.get(f"{prefix}hostName", "")),
            "port": str(SettingsManager.get(f"{prefix}port", "")),
            "user": str(SettingsManager.get(f"{prefix}user", "")),
            "password": str(SettingsManager.get(f"{prefix}password", "")),
        }

    def save_proxy_settings(
        self,
        *,
        enabled: bool,
        proxy_type: str,
        host: str,
        port: str,
        user: str,
        password: str,
    ) -> None:
        """Persist the sole application-wide proxy configuration."""
        prefix = self._GLOBAL_PROXY_PREFIX
        SettingsManager.set(f"{prefix}proxyEnable", bool(enabled))
        SettingsManager.set(f"{prefix}proxyType", str(proxy_type))
        SettingsManager.set(f"{prefix}hostName", str(host))
        SettingsManager.set(f"{prefix}port", str(port))
        SettingsManager.set(f"{prefix}user", str(user))
        SettingsManager.set(f"{prefix}password", str(password))

    def restore_proxy_settings(self) -> None:
        """Reset only the global proxy configuration."""
        self.save_proxy_settings(
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
        return self._privacy_settings.webrtc_shield_enabled

    @webrtc_shield_enabled.setter
    def webrtc_shield_enabled(self, value: bool) -> None:
        self._privacy_settings.webrtc_shield_enabled = value

    @property
    def strict_proxy_enabled(self) -> bool:
        """Whether strict proxy isolation was requested globally."""
        return self._privacy_settings.strict_proxy_enabled

    @strict_proxy_enabled.setter
    def strict_proxy_enabled(self, value: bool) -> None:
        self._privacy_settings.strict_proxy_enabled = value

    def apply_proxy(self) -> ProxyApplyResult:
        """Apply the currently persisted proxy configuration."""
        return ProxyManager.apply()
