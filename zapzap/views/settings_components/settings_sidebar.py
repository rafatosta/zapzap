from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout


class SettingsSidebarItem(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsNavButton")


class SettingsSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSidebar")
        self.setFixedWidth(240)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 18, 14, 18)
        self.layout.setSpacing(6)
        self.items = []

    def add_item(self, text):
        item = SettingsSidebarItem(text)
        self.items.append(item)
        self.layout.addWidget(item)
        return item

    def add_stretch(self):
        self.layout.addStretch(1)
