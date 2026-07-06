from __future__ import annotations

from enum import Enum
from typing import ClassVar
from typing import cast
from weakref import ref
from weakref import WeakMethod

from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

from zapzap.assets.themes.theme_stylesheet import ThemeStylesheet
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.theme.system_theme_monitor import SystemThemeMonitor


class ThemeManager(QObject):
    """Handles theme changes."""

    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    _QT_PALETTE_KEYS: ClassVar[set[str]] = {
        "window",
        "text",
        "base",
        "alternate_base",
        "button",
        "button_text",
        "highlight",
        "highlighted_text",
        "mid",
        "placeholder_text",
        "bright_text",
    }

    _LIGHT_PALETTE_COLORS: ClassVar[dict[str, str]] = {
        # Qt palette colors
        "window": "#f7f5f3",
        "text": "#1d1f1f",
        "base": "#ffffff",
        "alternate_base": "#eae9e7",
        "button": "#ffffff",
        "button_text": "#1d1f1f",
        "highlight": "#21c063",
        "highlighted_text": "#ffffff",
        "mid": "#D0D4D8",
        "placeholder_text": "#A6AEB6",
        "bright_text": "#e01b24",

        # Semantic colors
        "accent": "#21c063",
        "accent_text": "#ffffff",
        "accent_hover": "#1db356",
        "accent_border": "#1aa34e",

        "success": "#21c063",
        "success_text": "#ffffff",
        "success_hover": "#1db356",
        "success_border": "#1aa34e",

        "warning": "#cd9309",
        "warning_text": "#ffffff",
        "warning_hover": "#e5a50a",
        "warning_border": "#b58300",

        "danger": "#c01c28",
        "danger_text": "#ffffff",
        "danger_hover": "#e01b24",
        "danger_border": "#a51d2d",
    }

    _DARK_PALETTE_COLORS: ClassVar[dict[str, str]] = {
        # Qt palette colors
        "window": "#1d1f1f",
        "text": "#E1E1E1",
        "base": "#242626",
        "alternate_base": "#292a2a",
        "button": "#242626",
        "button_text": "#E1E1E1",
        "highlight": "#21c063",
        "highlighted_text": "#ffffff",
        "mid": "#444444",
        "placeholder_text": "#A6AEB6",
        "bright_text": "#ff6b6b",

        # Semantic colors
        "accent": "#21c063",
        "accent_text": "#ffffff",
        "accent_hover": "#25d366",
        "accent_border": "#1db356",

        "success": "#21c063",
        "success_text": "#ffffff",
        "success_hover": "#25d366",
        "success_border": "#1db356",

        "warning": "#e5a50a",
        "warning_text": "#1d1f1f",
        "warning_hover": "#f6d32d",
        "warning_border": "#cd9309",

        "danger": "#e01b24",
        "danger_text": "#ffffff",
        "danger_hover": "#ff4b55",
        "danger_border": "#c01c28",
    }

    theme_changed = pyqtSignal(object, object)

    _instance: ClassVar[ThemeManager | None] = None
    _creation_token: ClassVar[object] = object()

    def __init__(self, token=None, parent=None):
        """Initializes ThemeManager and loads theme settings."""
        if token is not type(self)._creation_token:
            raise RuntimeError(
                "ThemeManager is a singleton. Call ThemeManager.instance() "
                "instead of ThemeManager()."
            )

        super().__init__(parent)

        self._theme_observers = []
        self._current_color_scheme = Qt.ColorScheme.Unknown
        self._last_emitted_theme_state = None
        self._system_theme_monitor = SystemThemeMonitor(self)
        self._system_color_scheme = self._get_effective_system_color_scheme()

        self._system_theme_monitor.color_scheme_changed.connect(
            self._on_system_color_scheme_changed
        )

        try:
            theme = type(self).Type(
                SettingsManager.get("system/theme", type(self).Type.Auto.value)
            )
        except ValueError:
            # In case the legacy "custom" theme value is saved in the config file.
            theme = type(self).Type.Auto
            SettingsManager.set("system/theme", theme.value)

        self._current_theme = theme

        self._update_system_theme_monitor_state()
        self._apply_color_scheme()

    @classmethod
    def instance(cls) -> ThemeManager:
        """Returns the ThemeManager singleton instance."""
        # The singleton is enforced by a token instead of inside the __new__
        # method to avoid messing with the PyQt QObject lifetime management.

        if cls._instance is None:
            cls._instance = cls(
                token=cls._creation_token,
                parent=cls._get_app_instance(),
            )

        return cast(ThemeManager, cls._instance)

    @staticmethod
    def _get_app_instance() -> QApplication | None:
        return cast(QApplication | None, QApplication.instance())

    @classmethod
    def start(cls) -> ThemeManager:
        return cls.instance()

    @classmethod
    def stop(cls) -> None:
        if cls._instance is None:
            return

        cls._instance._system_theme_monitor.enabled = False
        cls._instance.deleteLater()
        cls._instance = None

    @classmethod
    def set_theme(cls, theme: Type | str) -> None:
        """Sets the ZapZap theme chosen by the user."""
        instance = cls.instance()
        theme = cls.Type(theme)

        if instance._current_theme == theme:
            return

        SettingsManager.set("system/theme", theme.value)

        if theme == cls.Type.Auto:
            instance._system_color_scheme = (
                instance._get_effective_system_color_scheme()
            )

        instance._current_theme = theme
        instance._update_system_theme_monitor_state()
        instance._apply_color_scheme()

    @classmethod
    def get_current_theme(cls) -> Type:
        """Returns the ZapZap theme currently selected by the user."""
        return cls.instance()._current_theme

    @classmethod
    def get_current_color_scheme(cls) -> Qt.ColorScheme:
        """Returns the effective current color scheme."""
        return cls.instance()._current_color_scheme

    @classmethod
    def get_current_palette_colors(cls) -> dict[str, str]:
        """Returns the active ZapZap palette colors, including semantic colors."""
        color_scheme = cls.get_current_color_scheme()

        if color_scheme == Qt.ColorScheme.Dark:
            return cls._DARK_PALETTE_COLORS.copy()

        return cls._LIGHT_PALETTE_COLORS.copy()

    @classmethod
    def get_color(cls, color_name: str, fallback: str = "") -> str:
        """Returns a color from the active ZapZap palette."""
        return cls.get_current_palette_colors().get(color_name, fallback)

    def _get_theme_color_scheme(self, theme: Type) -> Qt.ColorScheme:
        if theme == type(self).Type.Auto:
            return self._system_color_scheme

        return Qt.ColorScheme[theme.name]

    def _get_effective_system_color_scheme(self) -> Qt.ColorScheme:
        color_scheme = self._system_theme_monitor.get_current_color_scheme()

        if color_scheme == Qt.ColorScheme.Dark:
            return Qt.ColorScheme.Dark

        return Qt.ColorScheme.Light

    def _apply_color_scheme(self) -> None:
        current_color_scheme = self._get_theme_color_scheme(self._current_theme)
        self._current_color_scheme = current_color_scheme
        self._apply_palette_for_color_scheme(current_color_scheme)
        self._emit_theme_changed(self._current_theme, current_color_scheme)

    def add_theme_observer(self, callback) -> None:
        """Registers a callback to be called whenever the theme changes."""
        if getattr(callback, "__self__", None) is not None:
            self._theme_observers.append(WeakMethod(callback))
        else:
            self._theme_observers.append(ref(callback))

    def _notify_theme_observers(
        self,
        current_theme: Type,
        effective_color_scheme: Qt.ColorScheme,
    ) -> None:
        alive_observers = []

        for observer in self._theme_observers:
            callback = observer()

            if callback is not None:
                callback(current_theme, effective_color_scheme)
                alive_observers.append(observer)

        self._theme_observers = alive_observers

    def _emit_theme_changed(
        self,
        current_theme: Type,
        effective_color_scheme: Qt.ColorScheme,
    ) -> None:
        theme_state = (current_theme, effective_color_scheme)

        if self._last_emitted_theme_state != theme_state:
            self.theme_changed.emit(current_theme, effective_color_scheme)
            self._notify_theme_observers(current_theme, effective_color_scheme)
            self._last_emitted_theme_state = theme_state

    def _update_system_theme_monitor_state(self) -> None:
        self._system_theme_monitor.enabled = (
            self._current_theme == type(self).Type.Auto
        )

    def _on_system_color_scheme_changed(
        self,
        new_system_color_scheme: Qt.ColorScheme,
    ) -> None:
        if new_system_color_scheme == Qt.ColorScheme.Unknown:
            new_system_color_scheme = Qt.ColorScheme.Light

        if new_system_color_scheme == self._system_color_scheme:
            return

        self._system_color_scheme = new_system_color_scheme

        if self._current_theme == type(self).Type.Auto:
            self._apply_color_scheme()

    @staticmethod
    def _create_palette(colors: dict[str, str]) -> QPalette:
        palette = QPalette()

        palette.setColor(
            QPalette.ColorRole.Window,
            QColor(colors["window"]),
        )
        palette.setColor(
            QPalette.ColorRole.WindowText,
            QColor(colors["text"]),
        )
        palette.setColor(
            QPalette.ColorRole.Base,
            QColor(colors["base"]),
        )
        palette.setColor(
            QPalette.ColorRole.AlternateBase,
            QColor(colors["alternate_base"]),
        )
        palette.setColor(
            QPalette.ColorRole.ToolTipBase,
            QColor(colors["base"]),
        )
        palette.setColor(
            QPalette.ColorRole.ToolTipText,
            QColor(colors["text"]),
        )
        palette.setColor(
            QPalette.ColorRole.Text,
            QColor(colors["text"]),
        )
        palette.setColor(
            QPalette.ColorRole.Button,
            QColor(colors["button"]),
        )
        palette.setColor(
            QPalette.ColorRole.ButtonText,
            QColor(colors["button_text"]),
        )
        palette.setColor(
            QPalette.ColorRole.Highlight,
            QColor(colors["highlight"]),
        )
        palette.setColor(
            QPalette.ColorRole.HighlightedText,
            QColor(colors["highlighted_text"]),
        )
        palette.setColor(
            QPalette.ColorRole.Mid,
            QColor(colors["mid"]),
        )
        palette.setColor(
            QPalette.ColorRole.PlaceholderText,
            QColor(colors["placeholder_text"]),
        )
        palette.setColor(
            QPalette.ColorRole.BrightText,
            QColor(colors["bright_text"]),
        )

        return palette

    @classmethod
    def _get_qt_palette_colors(cls, colors: dict[str, str]) -> dict[str, str]:
        """Returns only colors that can be applied to QPalette."""
        return {
            key: value
            for key, value in colors.items()
            if key in cls._QT_PALETTE_KEYS
        }

    @classmethod
    def _get_palette_colors_for_color_scheme(
        cls,
        color_scheme: Qt.ColorScheme,
    ) -> dict[str, str]:
        if color_scheme == Qt.ColorScheme.Dark:
            return cls._DARK_PALETTE_COLORS

        return cls._LIGHT_PALETTE_COLORS

    @classmethod
    def _apply_palette_for_color_scheme(
        cls,
        color_scheme: Qt.ColorScheme,
    ) -> None:
        app = cls._get_app_instance()

        if app is None:
            return

        palette_colors = cls._get_palette_colors_for_color_scheme(color_scheme)
        qt_palette_colors = cls._get_qt_palette_colors(palette_colors)

        app.setPalette(cls._create_palette(qt_palette_colors))
        app.setStyleSheet(ThemeStylesheet.get_global_components_stylesheet())