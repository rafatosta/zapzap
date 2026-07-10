"""System startup and integration settings domain."""

from __future__ import annotations

from zapzap.core.config.settings.base import BaseSettings


class SystemSettings(BaseSettings):
    """Semantic access to system integration settings."""

    _WAYLAND = ("system/wayland", False)
    _CONFIRM_ON_CLOSE = ("system/confirm_on_close", False)
    _QUIT_ON_CLOSE = ("system/quit_in_close", False)
    _START_IN_BACKGROUND = ("system/start_background", False)
    _START_WITH_SYSTEM = ("system/start_system", False)
    _DONT_USE_NATIVE_DIALOG = ("system/DontUseNativeDialog", False)

    @property
    def wayland_enabled(self) -> bool:
        return self._get_bool(self._WAYLAND)

    @wayland_enabled.setter
    def wayland_enabled(self, value: bool) -> None:
        self._set_bool(self._WAYLAND, value)

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
