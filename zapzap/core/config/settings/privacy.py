"""Privacy settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class PrivacySettings(BaseSettings):
    """Semantic access to privacy settings."""

    _STRICT_PROXY = ("privacy/strict_proxy", False)

    @property
    def strict_proxy_enabled(self) -> bool:
        """Whether explicit proxies should block non-proxied WebRTC UDP."""
        return self._get_bool(self._STRICT_PROXY)

    @strict_proxy_enabled.setter
    def strict_proxy_enabled(self, value: bool) -> None:
        self._set_bool(self._STRICT_PROXY, value)
