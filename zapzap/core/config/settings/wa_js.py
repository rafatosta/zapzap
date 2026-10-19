"""WhatsApp Web WA-JS (experimental) settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class WaJsSettings(BaseSettings):
    """Semantic access to WhatsApp WA-JS bridge settings."""

    _ENABLED = ("wa_js/enabled", False)

    @property
    def enabled(self) -> bool:
        return self._get_bool(self._ENABLED)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_bool(self._ENABLED, bool(value))
