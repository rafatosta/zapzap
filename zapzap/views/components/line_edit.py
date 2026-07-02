"""ZapZap line edit component."""

from PyQt6.QtWidgets import QLineEdit

from .adaptive import AdaptiveStyleMixin, tokens


class LineEdit(AdaptiveStyleMixin, QLineEdit):
    """Theme-aware ZapZap line edit."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.install_adaptive_style()

    def apply_adaptive_style(self):
        c = tokens(self)
        self.setStyleSheet(f"""
            QLineEdit {{
                min-height: 36px;
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 6px 10px;
                background: {c['surface']};
                color: {c['text']};
                selection-background-color: {c['accent']};
            }}
            QLineEdit:hover {{
                border-color: {c['accent']};
                background: {c['surface_hover']};
            }}
            QLineEdit:focus {{
                border: 1px solid {c['accent']};
            }}
            QLineEdit:disabled, QLineEdit:read-only {{
                color: {c['muted']};
                background: {c['background']};
            }}
        """)
