from PyQt6.QtWidgets import QFrame


class SettingsDivider(QFrame):
    """Subtle separator used between rows in settings cards."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsDivider")
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setStyleSheet(
            "QFrame#SettingsDivider {"
            " color: palette(mid);"
            " max-height: 1px;"
            "}"
        )
