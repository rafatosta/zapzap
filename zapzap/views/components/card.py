"""ZapZap card component."""

from PyQt6.QtWidgets import QFrame, QVBoxLayout

from .adaptive import AdaptiveStyleMixin, tokens


class Card(AdaptiveStyleMixin, QFrame):
    """Theme-aware rounded card container."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ZapZapCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(0)
        self.install_adaptive_style()

    def add_widget(self, widget):
        self.layout.addWidget(widget)

    def apply_adaptive_style(self):
        c = tokens(self)
        self.setStyleSheet(f"""
            QFrame#ZapZapCard {{
                background: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 14px;
            }}
        """)
