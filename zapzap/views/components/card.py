"""ZapZap card component."""

from PyQt6.QtWidgets import QFrame, QVBoxLayout


class Card(QFrame):
    """Rounded card container styled from the active Qt palette."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ZapZapCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(0)
        self._apply_style()

    def add_widget(self, widget):
        self.layout.addWidget(widget)

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#ZapZapCard {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
        """)
