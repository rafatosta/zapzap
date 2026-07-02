
from PyQt6.QtWidgets import QComboBox

class ComboBox(QComboBox):
    """Combo box with the settings component object name for unified styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComboBox")