"""Performance settings domain."""

from __future__ import annotations

import logging
from typing import Any

from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.config.settings_manager import SettingsManager


logger = logging.getLogger(__name__)

INT32_MAX = (1 << 31) - 1
MEBIBYTE = 1024 * 1024
MAX_HTTP_CACHE_MIB = INT32_MAX // MEBIBYTE
AUTO_HTTP_CACHE_SIZE = 0
DEFAULT_HTTP_CACHE_TYPE = "DiskHttpCache"
HTTP_CACHE_TYPES = (
    "MemoryHttpCache",
    DEFAULT_HTTP_CACHE_TYPE,
    "NoCache",
)


def _normalize_http_cache_mib(value: Any) -> tuple[int, bool]:
    try:
        cache_mib = int(value)
    except (TypeError, ValueError, OverflowError):
        return AUTO_HTTP_CACHE_SIZE, False

    cache_bytes = cache_mib * MEBIBYTE
    if cache_mib < 0 or cache_bytes > INT32_MAX:
        return AUTO_HTTP_CACHE_SIZE, False

    return cache_mib, True


def normalize_http_cache_mib(value: Any) -> int:
    """Return a Qt-safe HTTP cache size in MiB, or automatic mode."""
    return _normalize_http_cache_mib(value)[0]


def http_cache_size_bytes(value: Any) -> int:
    """Convert a configured HTTP cache size to a Qt-safe byte count."""
    return normalize_http_cache_mib(value) * MEBIBYTE


def apply_http_cache_size(profile: Any, configured_value: Any) -> int:
    """Apply the cache limit without allowing this optimization to abort startup."""
    cache_mib = normalize_http_cache_mib(configured_value)
    cache_bytes = http_cache_size_bytes(cache_mib)

    try:
        profile.setHttpCacheMaximumSize(cache_bytes)
        return cache_mib
    except Exception:
        logger.exception(
            "Failed to apply HTTP cache size; falling back to automatic management"
        )

    try:
        profile.setHttpCacheMaximumSize(AUTO_HTTP_CACHE_SIZE)
    except Exception:
        logger.exception(
            "Failed to enable automatic HTTP cache management; continuing "
            "with the Qt profile default"
        )

    return AUTO_HTTP_CACHE_SIZE


def normalize_http_cache_type(value: Any) -> str:
    """Return a supported QWebEngineProfile cache type name."""
    return value if value in HTTP_CACHE_TYPES else DEFAULT_HTTP_CACHE_TYPE


def apply_http_cache_type(
    profile: Any,
    configured_value: Any,
    cache_types: dict[str, Any],
) -> str:
    """Apply a cache type and preserve startup if Qt rejects it."""
    cache_type = normalize_http_cache_type(configured_value)
    try:
        profile.setHttpCacheType(cache_types[cache_type])
        return cache_type
    except Exception:
        logger.exception(
            "Failed to apply HTTP cache type; falling back to disk cache"
        )

    try:
        profile.setHttpCacheType(cache_types[DEFAULT_HTTP_CACHE_TYPE])
    except Exception:
        logger.exception(
            "Failed to apply the HTTP cache type fallback; continuing "
            "with the Qt profile default"
        )
    return DEFAULT_HTTP_CACHE_TYPE


def apply_persistent_cookies_policy(
    profile: Any,
    enabled: bool,
    policies: dict[bool, Any],
) -> bool:
    """Apply cookie persistence and fall back to Qt's persistent policy."""
    desired = bool(enabled)
    try:
        profile.setPersistentCookiesPolicy(policies[desired])
        return desired
    except Exception:
        logger.exception(
            "Failed to apply the persistent cookies policy; falling back "
            "to Qt's persistent policy"
        )

    try:
        profile.setPersistentCookiesPolicy(policies[True])
    except Exception:
        logger.exception(
            "Failed to apply the persistent cookies policy fallback; "
            "continuing with the Qt profile default"
        )
    return True


class PerformanceSettings(BaseSettings):
    """Semantic access to Qt WebEngine/Chromium performance settings."""

    _CACHE_TYPE = ("performance/cache_type", DEFAULT_HTTP_CACHE_TYPE)
    _CACHE_SIZE_MAX = ("performance/cache_size_max", "0")
    _JS_MEMORY_LIMIT_INDEX = ("performance/js_memory_limit_index", 0)
    _LEGACY_JS_MEMORY_LIMIT_MB = ("performance/js_memory_limit_mb", "0")

    _BOOLEAN_SETTINGS = {
        "persistent_cookies": ("performance/persistent_cookies", True),
        "in_process_gpu": ("performance/in_process_gpu", False),
        "disable_gpu": ("performance/disable_gpu", False),
        "auto_gpu_workaround": ("performance/auto_gpu_workaround", True),
        "disable_gpu_vsync": ("performance/disable_gpu_vsync", False),
        "software_rendering": ("performance/software_rendering", False),
        "software_video_decoding": (
            "performance/software_video_decoding",
            False,
        ),
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
    JS_MEMORY_LIMIT_VALUES = (0, 256, 1024, 4096)

    @classmethod
    def _default_settings(cls) -> tuple[tuple[str, object], ...]:
        return (
            cls._CACHE_TYPE,
            cls._CACHE_SIZE_MAX,
            cls._JS_MEMORY_LIMIT_INDEX,
            cls._LEGACY_JS_MEMORY_LIMIT_MB,
            *cls._BOOLEAN_SETTINGS.values(),
        )

    def get_boolean_setting(self, name: str) -> bool:
        return bool(self._get(self._BOOLEAN_SETTINGS[name]))

    def set_boolean_setting(self, name: str, value: bool) -> None:
        self._set(self._BOOLEAN_SETTINGS[name], bool(value))

    @property
    def cache_type(self) -> str:
        raw_value = self._get(self._CACHE_TYPE)
        cache_type = normalize_http_cache_type(raw_value)
        if cache_type != raw_value:
            logger.warning(
                "Invalid stored HTTP cache type; replacing it with disk cache"
            )
            self._set_str(self._CACHE_TYPE, cache_type)
        return cache_type

    @cache_type.setter
    def cache_type(self, value: str) -> None:
        self._set_str(self._CACHE_TYPE, normalize_http_cache_type(value))

    @property
    def cache_size_max(self) -> int:
        raw_value = self._get(self._CACHE_SIZE_MAX)
        cache_mib, is_valid = _normalize_http_cache_mib(raw_value)
        if not is_valid:
            logger.warning(
                "Invalid stored HTTP cache size; replacing it with automatic "
                "management (accepted range: 0 to %d MiB)",
                MAX_HTTP_CACHE_MIB,
            )
            self._set_int(self._CACHE_SIZE_MAX, AUTO_HTTP_CACHE_SIZE)
        return cache_mib

    @cache_size_max.setter
    def cache_size_max(self, value: Any) -> None:
        cache_mib, is_valid = _normalize_http_cache_mib(value)
        if not is_valid:
            logger.warning(
                "Invalid HTTP cache size; storing automatic management "
                "(accepted range: 0 to %d MiB)",
                MAX_HTTP_CACHE_MIB,
            )
        self._set_int(self._CACHE_SIZE_MAX, cache_mib)

    @property
    def js_memory_limit_index(self) -> int:
        if not SettingsManager.contains(self._JS_MEMORY_LIMIT_INDEX[0]):
            legacy_value = self._get(self._LEGACY_JS_MEMORY_LIMIT_MB)
            try:
                legacy_mb = int(legacy_value)
                index = self.JS_MEMORY_LIMIT_VALUES.index(legacy_mb)
            except (TypeError, ValueError, OverflowError):
                index = 0
            self.js_memory_limit_index = index
            return index

        try:
            index = int(self._get(self._JS_MEMORY_LIMIT_INDEX))
            valid = True
        except (TypeError, ValueError, OverflowError):
            index = 0
            valid = False
        normalized = max(0, min(index, len(self.JS_MEMORY_LIMITS) - 1))
        if not valid or normalized != index:
            logger.warning(
                "Invalid stored JavaScript memory limit; replacing it with "
                "automatic management"
            )
            self.js_memory_limit_index = 0
            return 0
        return normalized

    @js_memory_limit_index.setter
    def js_memory_limit_index(self, value: int) -> None:
        try:
            index = int(value)
        except (TypeError, ValueError, OverflowError):
            index = 0
        if not 0 <= index < len(self.JS_MEMORY_LIMITS):
            index = 0
        self._set_int(self._JS_MEMORY_LIMIT_INDEX, index)
        self._set_int(
            self._LEGACY_JS_MEMORY_LIMIT_MB,
            self.JS_MEMORY_LIMIT_VALUES[index],
        )

    @property
    def js_memory_limit_mb(self) -> int:
        return self.JS_MEMORY_LIMIT_VALUES[self.js_memory_limit_index]

    def restore_defaults(self) -> None:
        for key, value in self._default_settings():
            SettingsManager.set(key, value)
