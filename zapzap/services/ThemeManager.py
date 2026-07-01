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

from zapzap.services.SystemThemeMonitor import SystemThemeMonitor
from zapzap.services.SettingsManager import SettingsManager


class ThemeManager(QObject):
    """Handles theme changes."""
    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    _LIGHT_PALETTE_COLORS = {
        "window": "#F0F2F5",
        "text": "#111B21",
        "base": "#FFFFFF",
        "alternate_base": "#F7F8FA",
        "button": "#FFFFFF",
        "button_text": "#111B21",
        "highlight": "#00A884",
        "highlighted_text": "#FFFFFF",
        "mid": "#DADDE1",
        "placeholder_text": "#667781",
        "bright_text": "#C1352B",
    }

    _DARK_PALETTE_COLORS = {
        "window": "#111B21",
        "text": "#E9EDEF",
        "base": "#202C33",
        "alternate_base": "#2A3942",
        "button": "#202C33",
        "button_text": "#E9EDEF",
        "highlight": "#00A884",
        "highlighted_text": "#111B21",
        "mid": "#2A3942",
        "placeholder_text": "#8696A0",
        "bright_text": "#FFB4AB",
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
            # In case the legacy "custom" theme value is saved in the config file
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

    def _get_theme_color_scheme(self, theme: Type) -> Qt.ColorScheme:
        if theme == type(self).Type.Auto:
            return self._system_color_scheme

        return Qt.ColorScheme[theme.name]

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
            instance._system_color_scheme = instance._get_effective_system_color_scheme()

        instance._current_theme = theme
        instance._update_system_theme_monitor_state()
        instance._apply_color_scheme()

    @classmethod
    def get_current_theme(cls) -> Type:
        """Returns the ZapZap theme currently selected by the user."""
        return cls.instance()._current_theme

    @classmethod
    def get_current_color_scheme(cls) -> Qt.ColorScheme:
        return cls.instance()._current_color_scheme

    def _get_effective_system_color_scheme(self) -> Qt.ColorScheme:
        color_scheme = self._system_theme_monitor.get_current_color_scheme()

        if color_scheme == Qt.ColorScheme.Dark:
            return Qt.ColorScheme.Dark

        return Qt.ColorScheme.Light

    def _apply_color_scheme(self) -> None:
        current_color_scheme = self._get_theme_color_scheme(
            self._current_theme)
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
        effective_color_scheme: Qt.ColorScheme
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
        effective_color_scheme: Qt.ColorScheme
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

    def _on_system_color_scheme_changed(self, new_system_color_scheme: Qt.ColorScheme) -> None:
        if new_system_color_scheme == Qt.ColorScheme.Unknown:
            new_system_color_scheme = Qt.ColorScheme.Light

        if new_system_color_scheme == self._system_color_scheme:
            return

        self._system_color_scheme = new_system_color_scheme

        if self._current_theme == type(self).Type.Auto:
            self._apply_color_scheme()

    @staticmethod
    def _create_palette(
        window: str,
        text: str,
        base: str,
        alternate_base: str,
        button: str,
        button_text: str,
        highlight: str,
        highlighted_text: str,
        mid: str,
        placeholder_text: str,
        bright_text: str,
    ) -> QPalette:
        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, QColor(window))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
        palette.setColor(QPalette.ColorRole.Base, QColor(base))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(alternate_base))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(base))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(text))
        palette.setColor(QPalette.ColorRole.Text, QColor(text))
        palette.setColor(QPalette.ColorRole.Button, QColor(button))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(button_text))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(highlighted_text))
        palette.setColor(QPalette.ColorRole.Mid, QColor(mid))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(placeholder_text))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(bright_text))

        return palette

    @classmethod
    def _apply_palette_for_color_scheme(cls, color_scheme: Qt.ColorScheme) -> None:
        app = cls._get_app_instance()
        if app is None:
            return

        palette_colors = (
            cls._DARK_PALETTE_COLORS
            if color_scheme == Qt.ColorScheme.Dark
            else cls._LIGHT_PALETTE_COLORS
        )

        app.setPalette(cls._create_palette(**palette_colors))
