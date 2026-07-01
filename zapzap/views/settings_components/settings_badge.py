from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class SettingsBadge(QLabel):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsBadge")
        colors = {"danger": ("#FEE2E2", "#DC2626"), "warning": ("#FEF3C7", "#D97706"), "success": ("#DCFCE7", "#16A34A"), "accent": ("#EEE9FF", "#6D4AFF")}
        bg, fg = colors.get(kind, colors["accent"])
        self.setStyleSheet(f"background: {bg}; color: {fg};")


class SettingsInfoBox(QFrame):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsInfoBox")
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
