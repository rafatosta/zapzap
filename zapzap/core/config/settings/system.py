"""System startup and integration settings domain."""

from __future__ import annotations

from enum import Enum

from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.config.settings_manager import SettingsManager


class DisplayBackend(str, Enum):
    """Qt platform backend selected before QApplication is created."""

    AUTO = "auto"
    WAYLAND = "wayland"
    XCB = "xcb"


class SystemSettings(BaseSettings):
    """Semantic access to system integration settings."""

    _WAYLAND = ("system/wayland", False)
    _DISPLAY_BACKEND = ("system/display_backend", DisplayBackend.AUTO.value)
    _CONFIRM_ON_CLOSE = ("system/confirm_on_close", False)
    _QUIT_ON_CLOSE = ("system/quit_in_close", False)
    _START_IN_BACKGROUND = ("system/start_background", False)
    _START_WITH_SYSTEM = ("system/start_system", False)
    _DONT_USE_NATIVE_DIALOG = ("system/DontUseNativeDialog", False)

    @property
    def wayland_enabled(self) -> bool:
        """Compatibility facade for the former Wayland boolean setting."""
        return self.display_backend == DisplayBackend.WAYLAND

    @wayland_enabled.setter
    def wayland_enabled(self, value: bool) -> None:
        self.display_backend = (
            DisplayBackend.WAYLAND if value else DisplayBackend.AUTO
        )

    @property
    def display_backend(self) -> DisplayBackend:
        """Return the explicit backend choice, migrating the legacy switch."""
        key, _default = self._DISPLAY_BACKEND
        if not SettingsManager.contains(key):
            backend = (
                DisplayBackend.WAYLAND
                if SettingsManager.contains(self._WAYLAND[0])
                and self._get_bool(self._WAYLAND)
                else DisplayBackend.AUTO
            )
            self.display_backend = backend
            return backend

        raw_value = self._get_str(self._DISPLAY_BACKEND)
        try:
            return DisplayBackend(raw_value)
        except ValueError:
            self.display_backend = DisplayBackend.AUTO
            return DisplayBackend.AUTO

    @display_backend.setter
    def display_backend(self, value: DisplayBackend | str) -> None:
        try:
            backend = DisplayBackend(value)
        except (TypeError, ValueError):
            backend = DisplayBackend.AUTO
        self._set_str(self._DISPLAY_BACKEND, backend.value)
        self._set_bool(self._WAYLAND, backend == DisplayBackend.WAYLAND)

    @property
    def confirm_on_close(self) -> bool:
        return self._get_bool(self._CONFIRM_ON_CLOSE)

    @confirm_on_close.setter
    def confirm_on_close(self, value: bool) -> None:
        self._set_bool(self._CONFIRM_ON_CLOSE, value)

    @property
    def quit_on_close(self) -> bool:
        return self._get_bool(self._QUIT_ON_CLOSE)

    @quit_on_close.setter
    def quit_on_close(self, value: bool) -> None:
        self._set_bool(self._QUIT_ON_CLOSE, value)

    @property
    def keep_running_in_background(self) -> bool:
        return not self.quit_on_close

    @keep_running_in_background.setter
    def keep_running_in_background(self, value: bool) -> None:
        self.quit_on_close = not value

    @property
    def start_in_background(self) -> bool:
        return self._get_bool(self._START_IN_BACKGROUND)

    @start_in_background.setter
    def start_in_background(self, value: bool) -> None:
        self._set_bool(self._START_IN_BACKGROUND, value)

    @property
    def start_with_system(self) -> bool:
        return self._get_bool(self._START_WITH_SYSTEM)

    @start_with_system.setter
    def start_with_system(self, value: bool) -> None:
        self._set_bool(self._START_WITH_SYSTEM, value)

    @property
    def dont_use_native_dialog(self) -> bool:
        return self._get_bool(self._DONT_USE_NATIVE_DIALOG)

    @dont_use_native_dialog.setter
    def dont_use_native_dialog(self, value: bool) -> None:
        self._set_bool(self._DONT_USE_NATIVE_DIALOG, value)
