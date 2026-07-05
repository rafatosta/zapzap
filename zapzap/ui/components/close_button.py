"""ZapZap close button component."""

from gettext import gettext as _

from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class CloseButton(QPushButton):
    """Small icon-only close button styled from the active Qt palette."""

    SIZE = 28
    FONT_SIZE = 16
    BORDER_RADIUS = 8

    STYLE = f"""
    QPushButton#ZapZapCloseButton {{
        min-width: {SIZE}px;
        min-height: {SIZE}px;
        max-width: {SIZE}px;
        max-height: {SIZE}px;
        border: 1px solid transparent;
        border-radius: {BORDER_RADIUS}px;
        padding: 0;
        background: transparent;
        color: palette(button-text);
        font-size: {FONT_SIZE}px;
        font-weight: 700;
    }}
    QPushButton#ZapZapCloseButton:hover {{
        background: palette(bright-text);
        border-color: palette(bright-text);
        color: palette(highlighted-text);
    }}
    QPushButton#ZapZapCloseButton:pressed {{
        background: palette(highlight);
        border-color: palette(highlight);
        color: palette(highlighted-text);
    }}
    QPushButton#ZapZapCloseButton:disabled {{
        background: transparent;
        border-color: transparent;
        color: palette(placeholder-text);
    }}
    """

    def __init__(self, parent=None, *, tooltip=None):
        super().__init__("×", parent)
        self.setObjectName("ZapZapCloseButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(QSize(self.SIZE, self.SIZE))
        self.setToolTip(tooltip or _("Close"))
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(self.STYLE)
