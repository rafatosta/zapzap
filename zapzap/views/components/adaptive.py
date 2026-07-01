"""Adaptive style primitives for ZapZap reusable components."""

from PyQt6.QtCore import QEvent
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette

from zapzap.services.ThemeManager import ThemeManager


LIGHT_TOKENS = {
    "background": "#F0F2F5",
    "surface": "#FFFFFF",
    "surface_hover": "#F7F8FA",
    "border": "#DADDE1",
    "text": "#111B21",
    "muted": "#667781",
    "accent": "#00A884",
    "accent_hover": "#06CF9C",
    "accent_soft": "#D9FDD3",
    "danger": "#C1352B",
}

DARK_TOKENS = {
    "background": "#111B21",
    "surface": "#202C33",
    "surface_hover": "#2A3942",
    "border": "#2A3942",
    "text": "#E9EDEF",
    "muted": "#8696A0",
    "accent": "#00A884",
    "accent_hover": "#06CF9C",
    "accent_soft": "#0B3B35",
    "danger": "#FFB4AB",
}


def _theme_name_from_color_scheme(color_scheme):
    if color_scheme == Qt.ColorScheme.Dark:
        return "dark"
    if color_scheme == Qt.ColorScheme.Light:
        return "light"
    return None


def is_dark(widget):
    """Return True when the component is using the dark theme."""
    adaptive_theme = getattr(widget, "_adaptive_theme", None)
    if adaptive_theme in {"dark", "light"}:
        return adaptive_theme == "dark"

    return widget.palette().color(QPalette.ColorRole.Window).lightness() < 128


def theme_name(widget):
    """Return the component theme name derived from the current Qt palette."""
    return "dark" if is_dark(widget) else "light"


def tokens(widget):
    """Return ZapZap component tokens for the widget's current theme."""
    return DARK_TOKENS if is_dark(widget) else LIGHT_TOKENS


class AdaptiveStyleMixin:
    """Mixin that updates a component style when Qt emits palette changes."""

    WATCHED_EVENTS = {
        QEvent.Type.ApplicationPaletteChange,
        QEvent.Type.PaletteChange,
    }

    def install_adaptive_style(self):
        self._adaptive_theme = theme_name(self)
        self.installEventFilter(self)
        if not getattr(self, "_adaptive_theme_signal_connected", False):
            ThemeManager.instance().add_theme_observer(self._handle_theme_changed)
            self._adaptive_theme_signal_connected = True
        self.apply_adaptive_style()

    def _refresh_adaptive_style(self, next_theme=None):
        next_theme = next_theme or theme_name(self)
        if next_theme != self._adaptive_theme:
            self._adaptive_theme = next_theme
        self.apply_adaptive_style()

    def _handle_theme_changed(self, _current_theme=None, effective_color_scheme=None):
        self._refresh_adaptive_style(_theme_name_from_color_scheme(effective_color_scheme))

    def eventFilter(self, watched, event):
        if watched is self and event.type() in self.WATCHED_EVENTS:
            self._refresh_adaptive_style()
        return super().eventFilter(watched, event)

    def apply_adaptive_style(self):
        """Apply the component-specific style."""
        raise NotImplementedError
