"""ZapZap button component."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class Button(QPushButton):
    """ZapZap push button styled from the active Qt palette."""

    DEFAULT = "default"
    WARNING = "warning"
    DANGER = "danger"

    def __init__(self, text="", variant=DEFAULT, parent=None):
        super().__init__(text, parent)

        self.variant = variant

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def set_variant(self, variant):
        """Change button visual variant."""

        self.variant = variant
        self._apply_style()

    def _apply_style(self):
        variants = {
            self.DEFAULT: {
                "border": "palette(mid)",
                "background": "palette(button)",
                "color": "palette(button-text)",
                "hover_border": "palette(highlight)",
                "hover_background": "palette(alternate-base)",
            },
            self.WARNING: {
                "border": "#d18b00",
                "background": "#fff3cd",
                "color": "#7a4f00",
                "hover_border": "#b87900",
                "hover_background": "#ffe8a1",
            },
            self.DANGER: {
                "border": "#dc3545",
                "background": "#f8d7da",
                "color": "#842029",
                "hover_border": "#b02a37",
                "hover_background": "#f1aeb5",
            },
        }

        style = variants.get(self.variant, variants[self.DEFAULT])

        self.setStyleSheet(f"""
            QPushButton {{
                min-height: 26px;
                border: 1px solid {style["border"]};
                border-radius: 8px;
                padding: 6px 12px;
                background: {style["background"]};
                color: {style["color"]};
            }}

            QPushButton:hover {{
                border-color: {style["hover_border"]};
                background: {style["hover_background"]};
            }}

            QPushButton:disabled {{
                color: palette(placeholder-text);
                background: palette(window);
                border-color: palette(mid);
            }}
        """)
