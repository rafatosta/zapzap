"""ZapZap button component."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from .adaptive import AdaptiveStyleMixin, tokens


class Button(AdaptiveStyleMixin, QPushButton):
    """Theme-aware ZapZap push button."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_adaptive_style()

    def apply_adaptive_style(self):
        c = tokens(self)
        self.setStyleSheet(f"""
            QPushButton {{
                min-height: 36px;
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 6px 12px;
                background: {c['surface']};
                color: {c['text']};
            }}
            QPushButton:hover {{
                border-color: {c['accent']};
                background: {c['accent_soft']};
            }}
            QPushButton:disabled {{
                color: {c['muted']};
                background: {c['background']};
            }}
        """)
