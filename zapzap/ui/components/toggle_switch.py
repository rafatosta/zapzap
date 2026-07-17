"""ZapZap toggle switch component."""

from PyQt6.QtCore import QEvent, QRectF, QSize, Qt
from PyQt6.QtGui import QPainter, QPalette
from PyQt6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):
    """WhatsApp-style pill toggle that paints from the active Qt palette."""

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("")
        self.setChecked(checked)
        self.setFixedSize(self.sizeHint())

    def sizeHint(self):
        return QSize(46, 26)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def changeEvent(self, event):
        if event.type() in {
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.PaletteChange,
            QEvent.Type.EnabledChange,
        }:
            self.update()
        super().changeEvent(event)

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
        palette = self.palette()
        knob_border = Qt.PenStyle.NoPen

        if self.isEnabled():
            if self.isChecked():
                track_color = palette.color(QPalette.ColorRole.Highlight)
                border_color = track_color
                knob_color = palette.color(QPalette.ColorRole.HighlightedText)
            else:
                track_color = palette.color(QPalette.ColorRole.Mid)
                border_color = palette.color(QPalette.ColorRole.Mid)
                knob_color = palette.color(QPalette.ColorRole.Base)
                knob_border = border_color
        else:
            track_color = palette.color(QPalette.ColorRole.Window)
            border_color = palette.color(QPalette.ColorRole.Mid)
            knob_color = palette.color(QPalette.ColorRole.PlaceholderText)

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
