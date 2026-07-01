from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class _BaseRow(QWidget):
    def __init__(self, title, description="", control=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)
        text = QWidget()
        text_layout = QHBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        labels = QWidget()
        labels_layout = QHBoxLayout(labels)
        labels_layout.setContentsMargins(0, 0, 0, 0)
        labels_layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setObjectName("SettingsRowTitle")
        labels_layout.addWidget(title_label)
        labels_layout.addStretch(1)
        text_layout.addWidget(labels)
        text_col = QWidget()
        from PyQt6.QtWidgets import QVBoxLayout
        col = QVBoxLayout(text_col)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(3)
        col.addWidget(title_label)
        if description:
            desc = QLabel(description)
            desc.setObjectName("SettingsRowDescription")
            desc.setWordWrap(True)
            col.addWidget(desc)
        layout.addWidget(text_col, 1)
        if control:
            layout.addWidget(control, 0, Qt.AlignmentFlag.AlignVCenter)
        self.control = control


class SettingsSwitchRow(_BaseRow):
    def __init__(self, title, description="", checked=False, parent=None):
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        super().__init__(title, description, self.checkbox, parent)


class SettingsSelectRow(_BaseRow):
    def __init__(self, title, description="", items=None, parent=None):
        self.combo = QComboBox()
        if items:
            self.combo.addItems(items)
        super().__init__(title, description, self.combo, parent)


class SettingsPathRow(_BaseRow):
    def __init__(self, title, description="", path="", button_text="Browse…", parent=None):
        box = QWidget()
        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = QLineEdit(path)
        self.button = QPushButton(button_text)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        super().__init__(title, description, box, parent)


class SettingsActionRow(_BaseRow):
    def __init__(self, title, description="", button_text="Open", parent=None):
        self.button = QPushButton(button_text)
        super().__init__(title, description, self.button, parent)


class SettingsTextRow(_BaseRow):
    def __init__(self, title, description="", text="", parent=None):
        self.line_edit = QLineEdit(text)
        super().__init__(title, description, self.line_edit, parent)


class SettingsPasswordRow(SettingsTextRow):
    def __init__(self, title, description="", text="", parent=None):
        super().__init__(title, description, text, parent)
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
