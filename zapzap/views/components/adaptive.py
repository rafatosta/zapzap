"""Adaptive style primitives for ZapZap reusable components."""

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtGui import QPalette


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


def is_dark(widget):
    """Return True when the current Qt palette is using a dark window color."""
    return widget.palette().color(QPalette.ColorRole.Window).lightness() < 128


def theme_name(widget):
    """Return the component theme name derived from the current Qt palette."""
    return "dark" if is_dark(widget) else "light"


def tokens(widget):
    """Return ZapZap component tokens for the widget's current palette."""
    return DARK_TOKENS if is_dark(widget) else LIGHT_TOKENS


def refresh_adaptive_styles(widget):
    """Reapply adaptive styles for a widget and all adaptive descendants."""
    children = [widget, *widget.findChildren(QObject)]
    for child in children:
        if isinstance(child, AdaptiveStyleMixin):
            child._adaptive_theme = theme_name(child)
            child.apply_adaptive_style()


class AdaptiveStyleMixin:
    """Mixin that updates a component style when Qt emits palette changes."""

    WATCHED_EVENTS = {
        QEvent.Type.ApplicationPaletteChange,
        QEvent.Type.PaletteChange,
    }

    def install_adaptive_style(self):
        self._adaptive_theme = theme_name(self)
        self.installEventFilter(self)
        self.apply_adaptive_style()

    def eventFilter(self, watched, event):
        if watched is self and event.type() in self.WATCHED_EVENTS:
            next_theme = theme_name(self)
            if next_theme != self._adaptive_theme:
                self._adaptive_theme = next_theme
                self.apply_adaptive_style()
        return super().eventFilter(watched, event)

    def apply_adaptive_style(self):
        """Apply the component-specific style."""
        raise NotImplementedError
