from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class SettingsBadge(QLabel):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsBadge")
        self.setProperty("kind", kind)


class SettingsInfoBox(QFrame):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsInfoBox")
        self.setProperty("kind", kind)
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
