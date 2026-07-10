"""Performance settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.config.settings_manager import SettingsManager


class PerformanceSettings(BaseSettings):
    """Semantic access to Qt WebEngine/Chromium performance settings."""

    _CACHE_TYPE = ("performance/cache_type", "DiskHttpCache")
    _CACHE_SIZE_MAX = ("performance/cache_size_max", "0")
    _JS_MEMORY_LIMIT_INDEX = ("performance/js_memory_limit_index", 0)

    _BOOLEAN_SETTINGS = {
        "persistent_cookies": ("performance/persistent_cookies", True),
        "in_process_gpu": ("performance/in_process_gpu", False),
        "disable_gpu": ("performance/disable_gpu", False),
        "disable_gpu_vsync": ("performance/disable_gpu_vsync", False),
        "software_rendering": ("performance/software_rendering", False),
        "force_gbm": ("performance/force_gbm", False),
        "disable_accessibility": ("performance/disable_accessibility", False),
        "single_process": ("performance/single_process", False),
        "process_per_site": ("performance/process_per_site", True),
        "js_predictable_gc_schedule": ("performance/js_predictable_gc_schedule", False),
        "scroll_animator": ("web/scroll_animator", False),
        "background_throttling": ("web/background_throttling", True),
        "disable_animations": ("web/disable_animations", False),
        "disable_pinch": ("web/disable_pinch", False),
        "ctrl_arrow_visual_navigation_fix": ("web/ctrl_arrow_visual_navigation_fix", True),
    }

    BOOLEAN_SETTINGS = tuple(_BOOLEAN_SETTINGS)
    JS_MEMORY_LIMITS = ("Automatic", "256 MB", "1024 MB", "4096 MB")

    @classmethod
    def _default_settings(cls) -> tuple[tuple[str, object], ...]:
        return (
            cls._CACHE_TYPE,
            cls._CACHE_SIZE_MAX,
            cls._JS_MEMORY_LIMIT_INDEX,
            *cls._BOOLEAN_SETTINGS.values(),
        )

    def get_boolean_setting(self, name: str) -> bool:
        return bool(self._get(self._BOOLEAN_SETTINGS[name]))

    def set_boolean_setting(self, name: str, value: bool) -> None:
        self._set(self._BOOLEAN_SETTINGS[name], bool(value))

    @property
    def cache_type(self) -> str:
        return self._get_str(self._CACHE_TYPE)

    @cache_type.setter
    def cache_type(self, value: str) -> None:
        self._set_str(self._CACHE_TYPE, value)

    @property
    def cache_size_max(self) -> str:
        return self._get_str(self._CACHE_SIZE_MAX)

    @cache_size_max.setter
    def cache_size_max(self, value: str) -> None:
        self._set_str(self._CACHE_SIZE_MAX, value)

    @property
    def js_memory_limit_index(self) -> int:
        try:
            index = int(self._get(self._JS_MEMORY_LIMIT_INDEX))
        except (TypeError, ValueError):
            index = 0
        return max(0, min(index, len(self.JS_MEMORY_LIMITS) - 1))

    @js_memory_limit_index.setter
    def js_memory_limit_index(self, value: int) -> None:
        self._set_int(self._JS_MEMORY_LIMIT_INDEX, value)

    def restore_defaults(self) -> None:
        for key, value in self._default_settings():
            SettingsManager.set(key, value)
