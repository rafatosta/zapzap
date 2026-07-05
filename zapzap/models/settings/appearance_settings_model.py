"""Model for appearance settings persistence."""

from __future__ import annotations

from zapzap.resources.CSRButtonThemeProvider import CSRButtonThemeProvider
from zapzap.resources.TrayIcon import TrayIcon
from zapzap.core.config.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.core.theme.ThemeManager import ThemeManager


class AppearanceSettingsModel:
    """Model for appearance settings persistence.

    This class hides SettingsManager keys from controllers and views.
    Controllers should access appearance settings only through semantic
    properties such as `browser_sidebar_visible`, `theme`, and `grid_columns`.
    """

    _BROWSER_SIDEBAR = ("system/sidebar", True)
    _MENUBAR = ("system/menubar", True)
    _SCALE = ("system/scale", 100)
    _TRAY_ICON = ("system/tray_icon", True)
    _NOTIFICATION_COUNTER = ("system/notificationCounter", False)
    _CSR_ENABLED = ("system/csr", False)
    _CSR_BUTTON_THEME = ("system/csr_button_theme", "default")
    _CSR_SHOW_MINIMIZE = ("system/csr_show_minimize_button", True)
    _CSR_SHOW_MAXIMIZE = ("system/csr_show_maximize_button", True)
    _CSR_BUTTONS_DIRECTION = ("system/csr_buttons_direction", "right")
    _THEME = ("system/theme", ThemeManager.Type.Auto.value)
    _TRAY_THEME = ("system/tray_theme", TrayIcon.Type.Default.value)
    _GRID_COLUMNS = ("system/grid_cols", 2)

    def _get_bool(self, setting: tuple[str, bool]) -> bool:
        key, default = setting
        return bool(SettingsManager.get(key, default))

    def _set_bool(self, setting: tuple[str, bool], value: bool) -> None:
        key, _default = setting
        SettingsManager.set(key, bool(value))

    def _get_str(self, setting: tuple[str, str]) -> str:
        key, default = setting
        return str(SettingsManager.get(key, default))

    def _set_str(self, setting: tuple[str, str], value: str) -> None:
        key, _default = setting
        SettingsManager.set(key, str(value))

    def _get_int(self, setting: tuple[str, int]) -> int:
        key, default = setting
        return int(SettingsManager.get(key, default))

    def _set_int(self, setting: tuple[str, int], value: int) -> None:
        key, _default = setting
        SettingsManager.set(key, int(value))

    @property
    def browser_sidebar_visible(self) -> bool:
        """Whether the browser sidebar is visible."""
        return self._get_bool(self._BROWSER_SIDEBAR)

    @browser_sidebar_visible.setter
    def browser_sidebar_visible(self, value: bool) -> None:
        self._set_bool(self._BROWSER_SIDEBAR, value)

    @property
    def menubar_visible(self) -> bool:
        """Whether the main window menu bar is visible."""
        return self._get_bool(self._MENUBAR)

    @menubar_visible.setter
    def menubar_visible(self, value: bool) -> None:
        self._set_bool(self._MENUBAR, value)

    @property
    def scale(self) -> int:
        """Interface scale percentage."""
        return self._get_int(self._SCALE)

    @scale.setter
    def scale(self, value: int) -> None:
        self._set_int(self._SCALE, value)

    @property
    def tray_icon_enabled(self) -> bool:
        """Whether the system tray icon is enabled."""
        return self._get_bool(self._TRAY_ICON)

    @tray_icon_enabled.setter
    def tray_icon_enabled(self, value: bool) -> None:
        self._set_bool(self._TRAY_ICON, value)

    @property
    def notification_counter_enabled(self) -> bool:
        """Whether unread count is shown on the tray icon."""
        return self._get_bool(self._NOTIFICATION_COUNTER)

    @notification_counter_enabled.setter
    def notification_counter_enabled(self, value: bool) -> None:
        self._set_bool(self._NOTIFICATION_COUNTER, value)

    @property
    def theme(self) -> str:
        """Current application theme preference."""
        return self._get_str(self._THEME)

    @theme.setter
    def theme(self, value: str) -> None:
        self._set_str(self._THEME, value)

    @property
    def tray_theme(self) -> str:
        """Current tray icon theme preference."""
        return self._get_str(self._TRAY_THEME)

    @tray_theme.setter
    def tray_theme(self, value: str) -> None:
        self._set_str(self._TRAY_THEME, value)

    @property
    def grid_columns(self) -> int:
        """Number of columns used by grid view."""
        return self._get_int(self._GRID_COLUMNS)

    @grid_columns.setter
    def grid_columns(self, value: int) -> None:
        self._set_int(self._GRID_COLUMNS, value)

    @property
    def csr_enabled(self) -> bool:
        """Whether custom window decoration is enabled."""
        return self._get_bool(self._CSR_ENABLED)

    @csr_enabled.setter
    def csr_enabled(self, value: bool) -> None:
        self._set_bool(self._CSR_ENABLED, value)

    @property
    def csr_button_theme(self) -> str:
        """Theme name used by custom window buttons."""
        return self._get_str(self._CSR_BUTTON_THEME).lower()

    @csr_button_theme.setter
    def csr_button_theme(self, value: str) -> None:
        self._set_str(self._CSR_BUTTON_THEME, value.lower())

    @property
    def csr_show_minimize_button(self) -> bool:
        """Whether CSR minimize button is visible."""
        return self._get_bool(self._CSR_SHOW_MINIMIZE)

    @csr_show_minimize_button.setter
    def csr_show_minimize_button(self, value: bool) -> None:
        self._set_bool(self._CSR_SHOW_MINIMIZE, value)

    @property
    def csr_show_maximize_button(self) -> bool:
        """Whether CSR maximize button is visible."""
        return self._get_bool(self._CSR_SHOW_MAXIMIZE)

    @csr_show_maximize_button.setter
    def csr_show_maximize_button(self, value: bool) -> None:
        self._set_bool(self._CSR_SHOW_MAXIMIZE, value)

    @property
    def csr_buttons_direction(self) -> str:
        """Side where CSR window buttons are placed."""
        direction = self._get_str(self._CSR_BUTTONS_DIRECTION).strip().lower()
        return "left" if direction == "left" else "right"

    @csr_buttons_direction.setter
    def csr_buttons_direction(self, value: str) -> None:
        direction = "left" if value.strip().lower() == "left" else "right"
        self._set_str(self._CSR_BUTTONS_DIRECTION, direction)

    def available_csr_button_themes(self) -> list[str]:
        """Return available CSR button theme names."""
        return CSRButtonThemeProvider.available_theme_names()

    def apply_theme(self, theme: ThemeManager.Type) -> None:
        """Apply the chosen application theme."""
        ThemeManager.set_theme(theme)

    def apply_tray_icon_enabled(self, enabled: bool) -> None:
        """Apply tray icon visibility through the tray manager."""
        SysTrayManager.set_state(enabled)

    def apply_tray_theme(self, tray_theme: TrayIcon.Type) -> None:
        """Apply the selected tray icon theme."""
        SysTrayManager.set_theme(tray_theme)

    def refresh_tray(self) -> None:
        """Refresh tray icon state after appearance changes."""
        SysTrayManager.refresh()
