"""Diagnostics settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class DiagnosticsSettings(BaseSettings):
    """Semantic access to diagnostics settings."""

    _PAGE_CONSOLE_LOG = ("diagnostics/page_console_log", True)

    @property
    def page_console_log_enabled(self) -> bool:
        return self._get_bool(self._PAGE_CONSOLE_LOG)

    @page_console_log_enabled.setter
    def page_console_log_enabled(self, value: bool) -> None:
        self._set_bool(self._PAGE_CONSOLE_LOG, value)
