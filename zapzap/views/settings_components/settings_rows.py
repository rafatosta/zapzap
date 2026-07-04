from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from zapzap.views.components import Button, ComboBox, Label, LineEdit, ToggleSwitch


class SettingsToggleSwitch(ToggleSwitch):
    """Settings-compatible toggle switch built from the generic component."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsToggleSwitch")


class _BaseRow(QWidget):
    def __init__(self, title, description="", control=None, parent=None, control_stretch=0):
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
        title_label = Label(title, "row_title")
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
            desc = Label(description, "row_description")
            desc.setObjectName("SettingsRowDescription")
            desc.setWordWrap(True)
            col.addWidget(desc)
        layout.addWidget(text_col, 1)
        if control:
            layout.addWidget(control, control_stretch, Qt.AlignmentFlag.AlignVCenter)
        self.control = control
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QLabel#SettingsRowTitle {
                font-weight: 600;
                color: palette(text);
            }
            QLabel#SettingsRowDescription {
                color: palette(placeholder-text);
            }
        """)


class SettingsSwitchRow(_BaseRow):
    def __init__(self, title, description="", checked=False, parent=None):
        self.checkbox = SettingsToggleSwitch()
        self.checkbox.setChecked(checked)
        super().__init__(title, description, self.checkbox, parent)


class SettingsComboBox(ComboBox):
    """Combo box with the settings component object name for unified styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsComboBox")


class SettingsSelectRow(_BaseRow):
    def __init__(self, title, description="", items=None, parent=None):
        self.combo = SettingsComboBox()
        if items:
            self.combo.addItems(items)
        super().__init__(title, description, self.combo, parent)


class SettingsPathRow(_BaseRow):
    def __init__(self, title, description="", path="", button_text="Browse…", parent=None):
        box = QWidget()
        box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = LineEdit(path)
        self.line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.button = Button(button_text)
        layout.addWidget(self.line_edit, 1)
        layout.addWidget(self.button)
        super().__init__(title, description, box, parent, control_stretch=1)


class SettingsActionRow(_BaseRow):
    def __init__(self, title, description="", button_text="Open", parent=None):
        self.button = Button(button_text)
        super().__init__(title, description, self.button, parent)


class SettingsTextRow(_BaseRow):
    def __init__(self, title, description="", text="", parent=None):
        self.line_edit = LineEdit(text)
        super().__init__(title, description, self.line_edit, parent)


class SettingsPasswordRow(SettingsTextRow):
    def __init__(self, title, description="", text="", parent=None):
        super().__init__(title, description, text, parent)
        self.line_edit.setEchoMode(LineEdit.EchoMode.Password)
