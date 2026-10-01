"""Model for appearance settings persistence."""

from __future__ import annotations

from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.assets.themes.csr_button_theme_provider import CSRButtonThemeProvider
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager


class AppearanceSettingsModel:
    """Model for appearance settings persistence.

    This class hides SettingsManager keys from controllers and views.
    Controllers should access appearance settings only through semantic
    properties such as `browser_sidebar_visible`, `theme`, and `grid_columns`.
    """

    def __init__(self) -> None:
        self._settings = AppearanceSettings()

    @property
    def browser_sidebar_visible(self) -> bool:
        """Whether the browser sidebar is visible."""
        return self._settings.browser_sidebar_visible

    @browser_sidebar_visible.setter
    def browser_sidebar_visible(self, value: bool) -> None:
        self._settings.browser_sidebar_visible = value

    @property
    def menubar_visible(self) -> bool:
        """Whether the main window menu bar is visible."""
        return self._settings.menubar_visible

    @menubar_visible.setter
    def menubar_visible(self, value: bool) -> None:
        self._settings.menubar_visible = value

    @property
    def scale(self) -> int:
        """Interface scale percentage."""
        return self._settings.scale

    @scale.setter
    def scale(self, value: int) -> None:
        self._settings.scale = value

    @property
    def tray_icon_enabled(self) -> bool:
        """Whether the system tray icon is enabled."""
        return self._settings.tray_icon_enabled

    @tray_icon_enabled.setter
    def tray_icon_enabled(self, value: bool) -> None:
        self._settings.tray_icon_enabled = value

    @property
    def notification_counter_enabled(self) -> bool:
        """Whether unread count is shown on the tray icon."""
        return self._settings.notification_counter_enabled

    @notification_counter_enabled.setter
    def notification_counter_enabled(self, value: bool) -> None:
        self._settings.notification_counter_enabled = value

    @property
    def theme(self) -> str:
        """Current application theme preference."""
        return self._settings.theme

    @theme.setter
    def theme(self, value: str) -> None:
        self._settings.theme = value

    @property
    def tray_theme(self) -> str:
        """Current tray icon theme preference."""
        return self._settings.tray_theme

    @tray_theme.setter
    def tray_theme(self, value: str) -> None:
        self._settings.tray_theme = value

    @property
    def grid_columns(self) -> int:
        """Number of columns used by grid view."""
        return self._settings.grid_columns

    @grid_columns.setter
    def grid_columns(self, value: int) -> None:
        self._settings.grid_columns = value

    @property
    def csr_enabled(self) -> bool:
        """Whether custom window decoration is enabled."""
        return self._settings.csr_enabled

    @csr_enabled.setter
    def csr_enabled(self, value: bool) -> None:
        self._settings.csr_enabled = value

    @property
    def csr_button_theme(self) -> str:
        """Theme name used by custom window buttons."""
        return self._settings.csr_button_theme

    @csr_button_theme.setter
    def csr_button_theme(self, value: str) -> None:
        self._settings.csr_button_theme = value

    @property
    def csr_show_minimize_button(self) -> bool:
        """Whether CSR minimize button is visible."""
        return self._settings.csr_show_minimize_button

    @csr_show_minimize_button.setter
    def csr_show_minimize_button(self, value: bool) -> None:
        self._settings.csr_show_minimize_button = value

    @property
    def csr_show_maximize_button(self) -> bool:
        """Whether CSR maximize button is visible."""
        return self._settings.csr_show_maximize_button

    @csr_show_maximize_button.setter
    def csr_show_maximize_button(self, value: bool) -> None:
        self._settings.csr_show_maximize_button = value

    @property
    def csr_buttons_direction(self) -> str:
        """Side where CSR window buttons are placed."""
        return self._settings.csr_buttons_direction

    @csr_buttons_direction.setter
    def csr_buttons_direction(self, value: str) -> None:
        self._settings.csr_buttons_direction = value

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
