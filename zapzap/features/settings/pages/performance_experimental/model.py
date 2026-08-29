"""Model for performance settings persistence."""

from __future__ import annotations

from zapzap.core.config.settings.performance import MAX_HTTP_CACHE_MIB
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings.performance import RenderingProfile


class PerformanceExperimentalSettingsModel:
    """Model for Qt WebEngine/Chromium performance settings."""

    CACHE_TYPES = [
        "DiskHttpCache",
        "MemoryHttpCache",
        "NoCache",
    ]
    CACHE_SIZES_MIB = (0, 128, 256, 512, 1024, MAX_HTTP_CACHE_MIB)
    JS_MEMORY_LIMITS = list(PerformanceSettings.JS_MEMORY_LIMITS)
    BOOLEAN_SETTINGS = PerformanceSettings.BOOLEAN_SETTINGS
    RENDERING_SETTINGS = PerformanceSettings.RENDERING_SETTINGS

    def __init__(self) -> None:
        self._settings = PerformanceSettings()

    def get_boolean_setting(self, name: str) -> bool:
        """Return a boolean performance setting by semantic name."""
        return self._settings.get_boolean_setting(name)

    def set_boolean_setting(self, name: str, value: bool) -> None:
        """Persist a boolean performance setting by semantic name."""
        self._settings.set_boolean_setting(name, value)

    @property
    def rendering_profile(self) -> RenderingProfile:
        """Return the profile detected from current rendering settings."""
        return self._settings.rendering_profile

    def apply_rendering_profile(self, profile: RenderingProfile) -> None:
        """Persist a predefined rendering profile."""
        self._settings.apply_rendering_profile(profile)

    @property
    def cache_type(self) -> str:
        return self._settings.cache_type

    @cache_type.setter
    def cache_type(self, value: str) -> None:
        self._settings.cache_type = value

    @property
    def cache_size_max(self) -> int:
        return self._settings.cache_size_max

    @cache_size_max.setter
    def cache_size_max(self, value: int) -> None:
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
