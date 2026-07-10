"""Spellcheck settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class SpellcheckSettings(BaseSettings):
    """Semantic access to spellcheck settings."""

    _ENABLED = ("system/spellCheckers", True)

    @property
    def enabled(self) -> bool:
        return self._get_bool(self._ENABLED)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._set_bool(self._ENABLED, value)
