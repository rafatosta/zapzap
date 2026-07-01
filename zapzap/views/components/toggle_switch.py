"""ZapZap toggle switch component."""

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QCheckBox

from .adaptive import AdaptiveStyleMixin, is_dark


class ToggleSwitch(AdaptiveStyleMixin, QCheckBox):
    """WhatsApp-style adaptive pill toggle."""

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("")
        self.setChecked(checked)
        self.setFixedSize(self.sizeHint())
        self.install_adaptive_style()

    def sizeHint(self):
        return QSize(46, 26)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def apply_adaptive_style(self):
        self.update()

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
        dark = is_dark(self)

        knob_border = Qt.PenStyle.NoPen
        if self.isEnabled():
            if self.isChecked():
                track_color = QColor("#25D366")
                border_color = QColor("#25D366")
                knob_color = QColor("#FFFFFF")
            elif dark:
                track_color = QColor("#2A3942")
                border_color = QColor("#3B4A54")
                knob_color = QColor("#8696A0")
            else:
                track_color = QColor("#F7F8FA")
                border_color = QColor("#D1D7DB")
                knob_color = QColor("#FFFFFF")
                knob_border = QColor("#D1D7DB")
        else:
            track_color = QColor("#2A3942" if dark else "#EEF0F2")
            border_color = QColor("#3B4A54" if dark else "#DADDE1")
            knob_color = QColor("#54656F" if dark else "#B0B7BD")

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
