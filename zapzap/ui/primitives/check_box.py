"""Reusable, palette-aware ZapZap check box primitive."""

from enum import Enum

from PyQt6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QCheckBox, QSizePolicy


class CheckBoxVariant(Enum):
    """Visual emphasis applied to a :class:`CheckBox`."""

    CLASSIC = "classic"
    SURFACE = "surface"
    SOFT = "soft"


class CheckBoxSize(Enum):
    """Density presets which retain a comfortable interaction target."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class CheckBoxTone(Enum):
    """Semantic color family used by a :class:`CheckBox`."""

    ACCENT = "accent"
    NEUTRAL = "neutral"


class CheckBox(QCheckBox):
    """Native checkbox behavior with scalable ZapZap vector painting."""

    DEFAULT_VARIANT = CheckBoxVariant.CLASSIC
    DEFAULT_SIZE = CheckBoxSize.MEDIUM
    DEFAULT_TONE = CheckBoxTone.ACCENT

    BORDER_WIDTH = 1.0
    FOCUS_WIDTH = 2.0
    FOCUS_PADDING = 3.0
    DISABLED_MIX = 0.58

    SIZE_TOKENS = {
        CheckBoxSize.SMALL: {
            "indicator": 16,
            "radius": 4,
            "spacing": 8,
            "hit_height": 28,
            "mark_width": 2.0,
        },
        CheckBoxSize.MEDIUM: {
            "indicator": 18,
            "radius": 5,
            "spacing": 10,
            "hit_height": 32,
            "mark_width": 2.2,
        },
        CheckBoxSize.LARGE: {
            "indicator": 22,
            "radius": 6,
            "spacing": 12,
            "hit_height": 38,
            "mark_width": 2.6,
        },
    }

    def __init__(
        self,
        text="",
        parent=None,
        *,
        variant=DEFAULT_VARIANT,
        size=DEFAULT_SIZE,
        tone=DEFAULT_TONE,
    ):
        super().__init__(text, parent)
        self._variant = CheckBoxVariant(variant)
        self._control_size = CheckBoxSize(size)
        self._tone = CheckBoxTone(tone)

        self.setObjectName("ZapCheckBox")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed,
        )
        self._apply_font()

    def variant(self):
        return self._variant

    def setVariant(self, variant):
        variant = CheckBoxVariant(variant)
        if variant != self._variant:
            self._variant = variant
            self.update()

    def controlSize(self):
        return self._control_size

    def setControlSize(self, size):
        size = CheckBoxSize(size)
        if size != self._control_size:
            self._control_size = size
            self.updateGeometry()
            self.update()

    def tone(self):
        return self._tone

    def setTone(self, tone):
        tone = CheckBoxTone(tone)
        if tone != self._tone:
            self._tone = tone
            self.update()

    def _apply_font(self):
        """Preserve the native body-text typography contract."""
        font = self.font()
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)

    def sizeHint(self):
        metrics = self._metrics()
        text_width = (
            self.fontMetrics().horizontalAdvance(self.text())
            if self.text()
            else 0
        )
        spacing = metrics["spacing"] if self.text() else 0
        outer_margin = self._outer_margin()
        width = (
            int(outer_margin * 2)
            + metrics["indicator"]
            + spacing
            + text_width
        )
        height = max(
            metrics["hit_height"],
            self.fontMetrics().height() + int(self.FOCUS_PADDING * 2),
        )
        return QSize(width, height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, position):
        """Keep the box and its complete label inside the click target."""
        return self.rect().contains(position)

    def indicatorRect(self):
        """Return the logical-pixel indicator geometry for tests/layout."""
        metrics = self._metrics()
        side = metrics["indicator"]
        y = (self.height() - side) / 2
        outer_margin = self._outer_margin()
        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            x = self.width() - outer_margin - side
        else:
            x = outer_margin
        return QRectF(x, y, side, side)

    def focusRect(self):
        return self.indicatorRect().adjusted(
            -self.FOCUS_PADDING,
            -self.FOCUS_PADDING,
            self.FOCUS_PADDING,
            self.FOCUS_PADDING,
        )

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = self._state_colors()
        indicator = self.indicatorRect()
        radius = self._metrics()["radius"]

        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(
                    colors["focus"],
                    self.FOCUS_WIDTH,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )
            painter.drawRoundedRect(
                self.focusRect(),
                radius + self.FOCUS_PADDING,
                radius + self.FOCUS_PADDING,
            )

        painter.setBrush(colors["background"])
        painter.setPen(
            QPen(
                colors["border"],
                self.BORDER_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawRoundedRect(indicator, radius, radius)

        state = self.checkState()
        if state == Qt.CheckState.Checked:
            self._draw_checkmark(painter, indicator, colors["mark"])
        elif state == Qt.CheckState.PartiallyChecked:
            self._draw_partial_mark(painter, indicator, colors["mark"])

        if self.text():
            painter.setPen(colors["text"])
            text_rect = self._text_rect(indicator)
            flags = (
                Qt.AlignmentFlag.AlignVCenter
                | Qt.AlignmentFlag.AlignLeft
                | Qt.TextFlag.TextShowMnemonic
            )
            if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
                flags = (
                    Qt.AlignmentFlag.AlignVCenter
                    | Qt.AlignmentFlag.AlignRight
                    | Qt.TextFlag.TextShowMnemonic
                )
            painter.drawText(text_rect, int(flags), self.text())

    def _draw_checkmark(self, painter, rect, color):
        path = QPainterPath()
        path.moveTo(
            QPointF(
                rect.left() + rect.width() * 0.23,
                rect.top() + rect.height() * 0.52,
            )
        )
        path.lineTo(
            QPointF(
                rect.left() + rect.width() * 0.43,
                rect.top() + rect.height() * 0.70,
            )
        )
        path.lineTo(
            QPointF(
                rect.left() + rect.width() * 0.79,
                rect.top() + rect.height() * 0.30,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(
                color,
                self._metrics()["mark_width"],
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawPath(path)

    def _draw_partial_mark(self, painter, rect, color):
        y = rect.center().y()
        painter.setPen(
            QPen(
                color,
                self._metrics()["mark_width"],
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(
            QPointF(rect.left() + rect.width() * 0.27, y),
            QPointF(rect.right() - rect.width() * 0.27, y),
        )

    def _text_rect(self, indicator):
        spacing = self._metrics()["spacing"]
        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            return QRectF(
                0,
                0,
                max(0, indicator.left() - spacing),
                self.height(),
            )
        left = indicator.right() + spacing
        return QRectF(left, 0, max(0, self.width() - left), self.height())

    def _state_colors(self):
        palette = self.palette()
        window = palette.window().color()
        base = palette.base().color()
        alternate = palette.alternateBase().color()
        text = palette.text().color()
        mid = palette.mid().color()
        placeholder = palette.placeholderText().color()
        accent = palette.highlight().color()
        accent_text = palette.highlightedText().color()

        checked = self.checkState() != Qt.CheckState.Unchecked
        interactive = self.isEnabled()
        hovered = interactive and self.underMouse()
        pressed = interactive and self.isDown()
        selected = accent if self._tone == CheckBoxTone.ACCENT else mid
        selected_text = (
            accent_text
            if self._tone == CheckBoxTone.ACCENT
            else self._contrast_color(selected, base, text)
        )

        if self._variant == CheckBoxVariant.CLASSIC:
            background = selected if checked else base
            border = selected if checked else mid
            mark = selected_text
        elif self._variant == CheckBoxVariant.SURFACE:
            background = (
                self._mix(selected, base, 0.76)
                if checked
                else alternate
            )
            border = self._mix(selected, mid, 0.62) if checked else mid
            mark = selected_text if checked else text
        else:
            background = (
                self._mix(selected, base, 0.28)
                if checked
                else self._mix(alternate, base, 0.88)
            )
            border = Qt.GlobalColor.transparent
            mark = (
                selected
                if self._tone == CheckBoxTone.ACCENT
                else placeholder
            )

        if hovered:
            border = selected
            background = self._mix(selected, background, 0.12)
        if pressed:
            background = self._mix(text, background, 0.16)

        if not interactive:
            background = self._mix(window, background, self.DISABLED_MIX)
            border = self._mix(window, border, self.DISABLED_MIX)
            mark = self._mix(placeholder, mark, 0.46)
            text = placeholder

        return {
            "background": QColor(background),
            "border": QColor(border),
            "mark": QColor(mark),
            "text": QColor(text),
            "focus": QColor(accent),
        }

    @staticmethod
    def _mix(first, second, amount):
        """Blend ``first`` into ``second`` using a bounded ratio."""
        amount = max(0.0, min(1.0, amount))
        first = QColor(first)
        second = QColor(second)
        return QColor(
            round(first.red() * amount + second.red() * (1 - amount)),
            round(first.green() * amount + second.green() * (1 - amount)),
            round(first.blue() * amount + second.blue() * (1 - amount)),
            round(first.alpha() * amount + second.alpha() * (1 - amount)),
        )

    @staticmethod
    def _contrast_color(background, light, dark):
        background = QColor(background)
        luminance = (
            background.red() * 0.299
            + background.green() * 0.587
            + background.blue() * 0.114
        )
        return QColor(dark if luminance > 150 else light)

    def _metrics(self):
        return self.SIZE_TOKENS[self._control_size]

    def _outer_margin(self):
        return self.FOCUS_PADDING + (self.FOCUS_WIDTH / 2)

    def changeEvent(self, event):
        if event.type() in {
            QEvent.Type.EnabledChange,
            QEvent.Type.FontChange,
            QEvent.Type.LayoutDirectionChange,
            QEvent.Type.PaletteChange,
        }:
            self.setCursor(
                Qt.CursorShape.PointingHandCursor
                if self.isEnabled()
                else Qt.CursorShape.ArrowCursor
            )
            self.updateGeometry()
            self.update()
        super().changeEvent(event)
