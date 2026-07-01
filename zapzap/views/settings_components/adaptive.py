"""Adaptive styling helpers for settings components."""

from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QPalette


WHATSAPP_LIGHT = {
    "background": "#F0F2F5",
    "card": "#FFFFFF",
    "border": "#DADDE1",
    "text": "#111B21",
    "muted": "#667781",
    "accent": "#00A884",
    "accent_hover": "#06CF9C",
    "accent_soft": "#D9FDD3",
    "button": "#FFFFFF",
}

WHATSAPP_DARK = {
    "background": "#111B21",
    "card": "#202C33",
    "border": "#2A3942",
    "text": "#E9EDEF",
    "muted": "#8696A0",
    "accent": "#00A884",
    "accent_hover": "#06CF9C",
    "accent_soft": "#0B3B35",
    "button": "#202C33",
}


def is_dark(widget):
    """Return True when the current Qt palette is using a dark window color."""
    return widget.palette().color(QPalette.ColorRole.Window).lightness() < 128


def theme_name(widget):
    """Return the current light/dark theme name for a widget."""
    return "dark" if is_dark(widget) else "light"


def theme_tokens(widget):
    """Return shared WhatsApp-inspired tokens for the widget palette."""
    return WHATSAPP_DARK if is_dark(widget) else WHATSAPP_LIGHT


class AdaptiveStyleMixin:
    """Mixin that reapplies a component style when Qt notifies palette changes."""

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
        """Apply component-specific style. Subclasses should override this."""
        raise NotImplementedError
