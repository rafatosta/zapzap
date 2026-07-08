"""Model for performance settings persistence."""

from __future__ import annotations

from zapzap.core.config.settings_manager import SettingsManager


class PerformanceExperimentalSettingsModel:
    """Model for Qt WebEngine/Chromium performance settings.

    This class centralizes the SettingsManager keys used by the performance page
    so controllers can work with semantic getter/setter methods.
    """

    DEFAULT_SETTINGS = {
        "performance/cache_type": "DiskHttpCache",
        "performance/cache_size_max": "0",
        "performance/persistent_cookies": True,
        "performance/in_process_gpu": False,
        "performance/disable_gpu": False,
        "performance/disable_gpu_vsync": False,
        "performance/software_rendering": False,
        "performance/force_gbm": False,
        "performance/disable_accessibility": False,
        "performance/single_process": False,
        "performance/process_per_site": True,
        "performance/js_memory_limit_index": 0,
        "performance/js_predictable_gc_schedule": False,
        "web/scroll_animator": False,
        "web/background_throttling": True,
        "web/disable_animations": False,
        "web/disable_pinch": False,
        "web/ctrl_arrow_visual_navigation_fix": True,
    }

    CACHE_TYPES = [
        "DiskHttpCache",
        "MemoryHttpCache",
        "NoCache",
    ]

    CACHE_SIZES = ["0 MB", "128 MB", "256 MB", "512 MB", "1024 MB", "2048 MB"]
    JS_MEMORY_LIMITS = ["Automatic", "256 MB", "1024 MB", "4096 MB"]

    def get(self, key: str):
        """Return a persisted performance setting using its safe default."""
        return SettingsManager.get(key, self.DEFAULT_SETTINGS[key])

    def set(self, key: str, value) -> None:
        """Persist a performance setting."""
        SettingsManager.set(key, value)

    def get_bool(self, key: str) -> bool:
        """Return a boolean performance setting."""
        return bool(self.get(key))

    def set_bool(self, key: str, value: bool) -> None:
        """Persist a boolean performance setting."""
        self.set(key, bool(value))

    @property
    def cache_type(self) -> str:
        return str(self.get("performance/cache_type"))

    @cache_type.setter
    def cache_type(self, value: str) -> None:
        self.set("performance/cache_type", value)

    @property
    def cache_size_max(self) -> str:
        return str(self.get("performance/cache_size_max"))

    @cache_size_max.setter
    def cache_size_max(self, value: str) -> None:
        self.set("performance/cache_size_max", value)

    @property
    def js_memory_limit_index(self) -> int:
        try:
            index = int(self.get("performance/js_memory_limit_index"))
        except (TypeError, ValueError):
            index = 0
        return max(0, min(index, len(self.JS_MEMORY_LIMITS) - 1))

    @js_memory_limit_index.setter
    def js_memory_limit_index(self, value: int) -> None:
        self.set("performance/js_memory_limit_index", int(value))

    def restore_defaults(self) -> None:
        """Restore all performance settings to safe defaults."""
        for key, value in self.DEFAULT_SETTINGS.items():
            SettingsManager.set(key, value)
