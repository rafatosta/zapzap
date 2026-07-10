"""Model for performance settings persistence."""

from __future__ import annotations

from zapzap.core.config.settings.performance import PerformanceSettings


class PerformanceExperimentalSettingsModel:
    """Model for Qt WebEngine/Chromium performance settings."""

    CACHE_TYPES = [
        "DiskHttpCache",
        "MemoryHttpCache",
        "NoCache",
    ]
    CACHE_SIZES = ["0 MB", "128 MB", "256 MB", "512 MB", "1024 MB", "2048 MB"]
    JS_MEMORY_LIMITS = list(PerformanceSettings.JS_MEMORY_LIMITS)
    BOOLEAN_SETTINGS = PerformanceSettings.BOOLEAN_SETTINGS

    def __init__(self) -> None:
        self._settings = PerformanceSettings()

    def get_boolean_setting(self, name: str) -> bool:
        """Return a boolean performance setting by semantic name."""
        return self._settings.get_boolean_setting(name)

    def set_boolean_setting(self, name: str, value: bool) -> None:
        """Persist a boolean performance setting by semantic name."""
        self._settings.set_boolean_setting(name, value)

    @property
    def cache_type(self) -> str:
        return self._settings.cache_type

    @cache_type.setter
    def cache_type(self, value: str) -> None:
        self._settings.cache_type = value

    @property
    def cache_size_max(self) -> str:
        return self._settings.cache_size_max

    @cache_size_max.setter
    def cache_size_max(self, value: str) -> None:
        self._settings.cache_size_max = value

    @property
    def js_memory_limit_index(self) -> int:
        return self._settings.js_memory_limit_index

    @js_memory_limit_index.setter
    def js_memory_limit_index(self, value: int) -> None:
        self._settings.js_memory_limit_index = value

    def restore_defaults(self) -> None:
        """Restore all performance settings to safe defaults."""
        self._settings.restore_defaults()
