from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class SettingsBadge(QLabel):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsBadge")
        self.set_kind(kind)

    def set_kind(self, kind):
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)


class SettingsInfoBox(QFrame):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsInfoBox")
        self.set_kind(kind)
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)

    def set_kind(self, kind):
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)
