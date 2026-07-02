from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPalette
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget

from zapzap.views.components import Button, ComboBox, LineEdit


class SettingsToggleSwitch(QCheckBox):
    """WhatsApp-style pill toggle used by settings switch rows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsToggleSwitch")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("")
        self.setFixedSize(self.sizeHint())

    def sizeHint(self):
        return QSize(46, 26)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def _is_dark(self):
        return self.palette().color(QPalette.ColorRole.Window).lightness() < 128

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin = 2
        track_rect = QRectF(
            margin,
            margin,
            self.width() - margin * 2,
            self.height() - margin * 2,
        )
        radius = track_rect.height() / 2

        knob_border = Qt.PenStyle.NoPen
        if self.isEnabled():
            if self.isChecked():
                track_color = QColor("#25D366")
                border_color = QColor("#25D366")
                knob_color = QColor("#FFFFFF")
            elif self._is_dark():
                track_color = QColor("#2A3942")
                border_color = QColor("#3B4A54")
                knob_color = QColor("#8696A0")
            else:
                track_color = QColor("#F7F8FA")
                border_color = QColor("#D1D7DB")
                knob_color = QColor("#FFFFFF")
                knob_border = QColor("#D1D7DB")
        else:
            track_color = QColor("#EEF0F2") if not self._is_dark() else QColor("#2A3942")
            border_color = QColor("#DADDE1") if not self._is_dark() else QColor("#3B4A54")
            knob_color = QColor("#B0B7BD") if not self._is_dark() else QColor("#54656F")

        painter.setPen(border_color)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, radius, radius)

        knob_diameter = self.height() - 8
        knob_y = (self.height() - knob_diameter) / 2
        knob_x = self.width() - knob_diameter - 5 if self.isChecked() else 5
        knob_rect = QRectF(knob_x, knob_y, knob_diameter, knob_diameter)
        painter.setPen(knob_border)
        painter.setBrush(knob_color)
        painter.drawEllipse(knob_rect)


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
        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = LineEdit(path)
        self.button = Button(button_text)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        super().__init__(title, description, box, parent)


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
