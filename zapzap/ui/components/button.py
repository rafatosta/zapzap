"""ZapZap button component."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from zapzap.core.theme.theme_manager import ThemeManager


class Button(QPushButton):
    """ZapZap push button styled from the active ZapZap palette."""

    DEFAULT = "default"
    WARNING = "warning"
    DANGER = "danger"

    def __init__(self, text="", variant=DEFAULT, parent=None):
        super().__init__(text, parent)

        self.variant = variant

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def set_variant(self, variant):
        """Change button visual variant."""

        self.variant = variant
        self._apply_style()

    def _on_theme_changed(self, *_args):
        """Refresh button style when the application theme changes."""

        self._apply_style()

    def _get_variant_style(self):
        """Return stylesheet tokens for the current button variant."""

        variants = {
            self.DEFAULT: {
                "border": "palette(mid)",
                "background": "palette(button)",
                "color": "palette(button-text)",
                "hover_border": "palette(highlight)",
                "hover_background": "palette(alternate-base)",
            },
            self.WARNING: {
                "border": "palette(mid)",
                "background": "palette(button)",
                "color": ThemeManager.get_color("warning"),
                "hover_border": ThemeManager.get_color("warning_hover"),
                
            },
            self.DANGER: {
                "border": "palette(mid)",
                "background": "palette(button)",
                "color": ThemeManager.get_color("bright_text"),
                "hover_border": ThemeManager.get_color("danger_hover"),
                "hover_background": "palette(alternate-base)",
            },
        }

        return variants.get(self.variant, variants[self.DEFAULT])

    def _apply_style(self):
        style = self._get_variant_style()

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
               
            }}

            QPushButton:disabled {{
                color: palette(placeholder-text);
                background: palette(window);
                border-color: palette(mid);
            }}
        """)
