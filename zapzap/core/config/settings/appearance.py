"""Appearance settings domain."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QPoint

from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.theme.theme_manager import ThemeManager


logger = logging.getLogger(__name__)
DEFAULT_SCALE = 100
MIN_SCALE = 1
MAX_SCALE = 1000


class AppearanceSettings(BaseSettings):
    """Semantic access to appearance and layout settings."""

    _BROWSER_SIDEBAR = ("system/sidebar", True)
    _MENUBAR = ("system/menubar", True)
    _SCALE = ("system/scale", DEFAULT_SCALE)
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
    _FLOATING_MONITORING_PANEL_ENABLED = (
        "system/floating_monitoring_panel_enabled",
        False,
    )
    _INTEGRATED_ACCOUNT_SELECTOR_ENABLED = (
        "system/integrated_account_selector_enabled",
        False,
    )
    _COMPACT_CHAT_LIST_ENABLED = ("system/compact_chat_list_enabled", False)
    _RESIZABLE_CHAT_LIST_ENABLED = (
        "system/resizable_chat_list_enabled",
        False,
    )

    _FLOATING_MODE = ("system/floating_monitoring_panel_mode", "always")
    _FLOATING_ON_TOP = ("system/floating_monitoring_panel_on_top", False)
    _FLOATING_REMEMBER_POSITION = (
        "system/floating_monitoring_panel_remember_position", True,
    )
    _FLOATING_LOCK_POSITION = (
        "system/floating_monitoring_panel_lock_position", False,
    )
    _FLOATING_POSITION = ("system/floating_monitoring_panel_position", None)
    FLOATING_MODES = ("always", "when_hidden", "on_demand")

    @property
    def floating_panel_mode(self) -> str:
        value = self._get(self._FLOATING_MODE)
        return value if value in self.FLOATING_MODES else "always"

    @floating_panel_mode.setter
    def floating_panel_mode(self, value: str) -> None:
        self._set_str(
            self._FLOATING_MODE, value if value in self.FLOATING_MODES else "always"
        )

    @property
    def floating_panel_on_top(self) -> bool:
        return self._get_bool(self._FLOATING_ON_TOP)

    @floating_panel_on_top.setter
    def floating_panel_on_top(self, value: bool) -> None:
        self._set_bool(self._FLOATING_ON_TOP, value)

    @property
    def floating_panel_remember_position(self) -> bool:
        return self._get_bool(self._FLOATING_REMEMBER_POSITION)

    @floating_panel_remember_position.setter
    def floating_panel_remember_position(self, value: bool) -> None:
        self._set_bool(self._FLOATING_REMEMBER_POSITION, value)

    @property
    def floating_panel_lock_position(self) -> bool:
        return self._get_bool(self._FLOATING_LOCK_POSITION)

    @floating_panel_lock_position.setter
    def floating_panel_lock_position(self, value: bool) -> None:
        self._set_bool(self._FLOATING_LOCK_POSITION, value)

    @property
    def floating_panel_position(self) -> QPoint | None:
        value = self._get(self._FLOATING_POSITION)
        return QPoint(value) if isinstance(value, QPoint) else None

    @floating_panel_position.setter
    def floating_panel_position(self, value: QPoint | None) -> None:
        self._set(
            self._FLOATING_POSITION,
            QPoint(value) if isinstance(value, QPoint) else None,
        )

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
        raw_value = self._get(self._SCALE)
        try:
            scale = int(raw_value)
        except (TypeError, ValueError, OverflowError):
            scale = DEFAULT_SCALE
        if not MIN_SCALE <= scale <= MAX_SCALE:
            scale = DEFAULT_SCALE
        if scale != raw_value:
            logger.warning(
                "Invalid stored interface scale; replacing it with 100 percent"
            )
            self._set_int(self._SCALE, scale)
        return scale

    @scale.setter
    def scale(self, value: Any) -> None:
        try:
            scale = int(value)
        except (TypeError, ValueError, OverflowError):
            scale = DEFAULT_SCALE
        self._set_int(
            self._SCALE,
            scale if MIN_SCALE <= scale <= MAX_SCALE else DEFAULT_SCALE,
        )

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
        raw_value = self._get(self._TRAY_THEME)
        valid_values = {item.value for item in TrayIcon.Type}
        tray_theme = (
            raw_value
            if isinstance(raw_value, str) and raw_value in valid_values
            else TrayIcon.Type.Default.value
        )
        if tray_theme != raw_value:
            logger.warning(
                "Invalid stored tray icon theme; replacing it with the default"
            )
            self._set_str(self._TRAY_THEME, tray_theme)
        return tray_theme

    @tray_theme.setter
    def tray_theme(self, value: str) -> None:
        valid_values = {item.value for item in TrayIcon.Type}
        tray_theme = (
            value
            if isinstance(value, str) and value in valid_values
            else TrayIcon.Type.Default.value
        )
        self._set_str(self._TRAY_THEME, tray_theme)

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

    @property
    def floating_monitoring_panel_enabled(self) -> bool:
        """Whether the floating monitoring panel preference is enabled."""
        return self._get_bool(self._FLOATING_MONITORING_PANEL_ENABLED)

    @floating_monitoring_panel_enabled.setter
    def floating_monitoring_panel_enabled(self, value: bool) -> None:
        self._set_bool(self._FLOATING_MONITORING_PANEL_ENABLED, value)

    @property
    def integrated_account_selector_enabled(self) -> bool:
        """Whether the integrated account selector preference is enabled."""
        return self._get_bool(self._INTEGRATED_ACCOUNT_SELECTOR_ENABLED)

    @integrated_account_selector_enabled.setter
    def integrated_account_selector_enabled(self, value: bool) -> None:
        self._set_bool(self._INTEGRATED_ACCOUNT_SELECTOR_ENABLED, value)

    @property
    def resizable_chat_list_enabled(self) -> bool:
        """Whether the WhatsApp Web chat list can be resized by dragging."""
        return self._get_bool(self._RESIZABLE_CHAT_LIST_ENABLED)

    @resizable_chat_list_enabled.setter
    def resizable_chat_list_enabled(self, value: bool) -> None:
        self._set_bool(self._RESIZABLE_CHAT_LIST_ENABLED, value)

    @property
    def compact_chat_list_enabled(self) -> bool:
        """Whether the chat list shows only avatars at a fixed width."""
        return self._get_bool(self._COMPACT_CHAT_LIST_ENABLED)

    @compact_chat_list_enabled.setter
    def compact_chat_list_enabled(self, value: bool) -> None:
        self._set_bool(self._COMPACT_CHAT_LIST_ENABLED, value)
