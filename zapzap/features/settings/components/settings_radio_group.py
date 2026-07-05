"""Grouped radio button container for settings pages."""

from PyQt6.QtWidgets import QVBoxLayout, QWidget


class SettingsRadioGroup(QWidget):
    """Adwaita-inspired vertical group for settings radio buttons."""

    def __init__(self, *radio_buttons, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsRadioGroup")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._radio_buttons = []
        for radio_button in radio_buttons:
            self.add_radio_button(radio_button)
        self._apply_style()

    def add_radio_button(self, radio_button):
        """Add a radio button and refresh first/last styling metadata."""
        self._radio_buttons.append(radio_button)
        self.layout.addWidget(radio_button)
        self._refresh_button_positions()

    def _refresh_button_positions(self):
        last_index = len(self._radio_buttons) - 1
        for index, radio_button in enumerate(self._radio_buttons):
            radio_button.setProperty("first", index == 0)
            radio_button.setProperty("last", index == last_index)
            radio_button.style().unpolish(radio_button)
            radio_button.style().polish(radio_button)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#SettingsRadioGroup {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
            QWidget#SettingsRadioGroup QRadioButton#ZapRadioButton {
                border-bottom: 1px solid palette(mid);
            }
            QWidget#SettingsRadioGroup QRadioButton#ZapRadioButton[last="true"] {
                border-bottom: 0;
            }
        """)
