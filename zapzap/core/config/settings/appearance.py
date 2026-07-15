"""Appearance settings domain."""

from __future__ import annotations

from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.theme.theme_manager import ThemeManager


class AppearanceSettings(BaseSettings):
    """Semantic access to appearance and layout settings."""

    _BROWSER_SIDEBAR = ("system/sidebar", True)
    _MENUBAR = ("system/menubar", True)
    _SCALE = ("system/scale", 100)
    _TRAY_ICON = ("system/tray_icon", True)
    _NOTIFICATION_COUNTER = ("system/notificationCounter", True)
    _CSR_ENABLED = ("system/csr", False)
    _CSR_BUTTON_THEME = ("system/csr_button_theme", "default")
    _CSR_SHOW_MINIMIZE = ("system/csr_show_minimize_button", True)
    _CSR_SHOW_MAXIMIZE = ("system/csr_show_maximize_button", True)
    _CSR_BUTTONS_DIRECTION = ("system/csr_buttons_direction", "right")
    _THEME = ("system/theme", ThemeManager.Type.Auto.value)
    _TRAY_THEME = ("system/tray_theme", TrayIcon.Type.Default.value)
    _GRID_COLUMNS = ("system/grid_cols", 2)

    @property
    def browser_sidebar_visible(self) -> bool:
        return self._get_bool(self._BROWSER_SIDEBAR)

    @browser_sidebar_visible.setter
    def browser_sidebar_visible(self, value: bool) -> None:
        self._set_bool(self._BROWSER_SIDEBAR, value)

    @property
    def menubar_visible(self) -> bool:
        return self._get_bool(self._MENUBAR)

    @menubar_visible.setter
    def menubar_visible(self, value: bool) -> None:
        self._set_bool(self._MENUBAR, value)

    @property
    def scale(self) -> int:
        return self._get_int(self._SCALE)

    @scale.setter
    def scale(self, value: int) -> None:
        self._set_int(self._SCALE, value)

    @property
    def tray_icon_enabled(self) -> bool:
        return self._get_bool(self._TRAY_ICON)

    @tray_icon_enabled.setter
    def tray_icon_enabled(self, value: bool) -> None:
        self._set_bool(self._TRAY_ICON, value)

    @property
    def notification_counter_enabled(self) -> bool:
        return self._get_bool(self._NOTIFICATION_COUNTER)

    @notification_counter_enabled.setter
    def notification_counter_enabled(self, value: bool) -> None:
        self._set_bool(self._NOTIFICATION_COUNTER, value)

    @property
    def theme(self) -> str:
        return self._get_str(self._THEME)

    @theme.setter
    def theme(self, value: str) -> None:
        self._set_str(self._THEME, value)

    @property
    def tray_theme(self) -> str:
        return self._get_str(self._TRAY_THEME)

    @tray_theme.setter
    def tray_theme(self, value: str) -> None:
        self._set_str(self._TRAY_THEME, value)

    @property
    def grid_columns(self) -> int:
        return self._get_int(self._GRID_COLUMNS)

    @grid_columns.setter
    def grid_columns(self, value: int) -> None:
        self._set_int(self._GRID_COLUMNS, value)

    @property
    def csr_enabled(self) -> bool:
        return self._get_bool(self._CSR_ENABLED)

    @csr_enabled.setter
    def csr_enabled(self, value: bool) -> None:
        self._set_bool(self._CSR_ENABLED, value)

    @property
    def csr_button_theme(self) -> str:
        return self._get_str(self._CSR_BUTTON_THEME).lower()

    @csr_button_theme.setter
    def csr_button_theme(self, value: str) -> None:
        self._set_str(self._CSR_BUTTON_THEME, value.lower())

    @property
    def csr_show_minimize_button(self) -> bool:
        return self._get_bool(self._CSR_SHOW_MINIMIZE)

    @csr_show_minimize_button.setter
    def csr_show_minimize_button(self, value: bool) -> None:
        self._set_bool(self._CSR_SHOW_MINIMIZE, value)

    @property
    def csr_show_maximize_button(self) -> bool:
        return self._get_bool(self._CSR_SHOW_MAXIMIZE)

    @csr_show_maximize_button.setter
    def csr_show_maximize_button(self, value: bool) -> None:
        self._set_bool(self._CSR_SHOW_MAXIMIZE, value)

    @property
    def csr_buttons_direction(self) -> str:
        direction = self._get_str(self._CSR_BUTTONS_DIRECTION).strip().lower()
        return "left" if direction == "left" else "right"

    @csr_buttons_direction.setter
    def csr_buttons_direction(self, value: str) -> None:
        direction = "left" if value.strip().lower() == "left" else "right"
        self._set_str(self._CSR_BUTTONS_DIRECTION, direction)
