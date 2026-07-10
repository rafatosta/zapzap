"""Shared helpers for semantic settings domains."""

from __future__ import annotations

from typing import Any

from zapzap.core.config.settings_manager import SettingsManager


class BaseSettings:
    """Base class for typed access to SettingsManager entries."""

    @staticmethod
    def _get(setting: tuple[str, Any]) -> Any:
        key, default = setting
        return SettingsManager.get(key, default)

    @staticmethod
    def _set(setting: tuple[str, Any], value: Any) -> None:
        key, _default = setting
        SettingsManager.set(key, value)

    @staticmethod
    def _get_bool(setting: tuple[str, bool]) -> bool:
        return bool(BaseSettings._get(setting))

    @staticmethod
    def _set_bool(setting: tuple[str, bool], value: bool) -> None:
        BaseSettings._set(setting, bool(value))

    @staticmethod
    def _get_int(setting: tuple[str, int]) -> int:
        return int(BaseSettings._get(setting))

    @staticmethod
    def _set_int(setting: tuple[str, int], value: int) -> None:
        BaseSettings._set(setting, int(value))

    @staticmethod
    def _get_str(setting: tuple[str, str]) -> str:
        return str(BaseSettings._get(setting))

    @staticmethod
    def _set_str(setting: tuple[str, str], value: str) -> None:
        BaseSettings._set(setting, str(value))
