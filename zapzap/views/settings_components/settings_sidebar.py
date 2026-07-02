from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout


class SettingsSidebarItem(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsNavButton")
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton#SettingsNavButton {
                border: 0;
                border-radius: 10px;
                padding: 10px 12px;
                text-align: left;
                color: palette(text);
                background: transparent;
                font-weight: 500;
            }
            QPushButton#SettingsNavButton:hover {
                background: palette(alternate-base);
                color: palette(text);
            }
            QPushButton#SettingsNavButton:disabled {
                background: palette(alternate-base);
                color: palette(highlight);
            }
        """)


class SettingsSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSidebar")
        self.setFixedWidth(240)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 18, 14, 18)
        self.layout.setSpacing(6)
        self.items = []
        self._apply_style()

    def add_item(self, text):
        item = SettingsSidebarItem(text)
        self.items.append(item)
        self.layout.addWidget(item)
        return item

    def add_stretch(self):
        self.layout.addStretch(1)

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#SettingsSidebar {
                background: palette(base);
                border-right: 1px solid palette(mid);
            }
        """)
