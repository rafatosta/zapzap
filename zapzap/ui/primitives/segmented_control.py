"""Reusable exclusive segmented-control primitive."""

from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import QEvent, QLineF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QPalette, QPen
from PyQt6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

from zapzap.ui.typography import Typography


@dataclass(frozen=True)
class SegmentOption:
    """One stable value and its translated presentation label."""

    value: object
    label: str
    enabled: bool = True


class SegmentedControlSize(Enum):
    """Reusable control density variants."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class SegmentedControlRadius(Enum):
    """Reusable outer corner-radius variants."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    FULL = "full"


@dataclass(frozen=True)
class _SizeMetrics:
    minimum_height: int
    horizontal_padding: int
    vertical_padding: int
    minimum_segment_width: int
    font_size: int


class _SegmentButton(QAbstractButton):
    """Internal native button used for mouse and accessibility semantics."""

    def __init__(self, control, index, option):
        super().__init__(control)
        self._control = control
        self.index = index
        self.setText(option.label)
        self.setAccessibleName(option.label)
        self.setCheckable(True)
        self.setEnabled(option.enabled)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if option.enabled
            else Qt.CursorShape.ArrowCursor
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def sizeHint(self):
        return self._control._segment_size_hint(self.index)

    def minimumSizeHint(self):
        return self.sizeHint()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.EnabledChange:
            self.setCursor(
                Qt.CursorShape.PointingHandCursor
                if self.isEnabled() and self._control.isEnabled()
                else Qt.CursorShape.ArrowCursor
            )
        super().changeEvent(event)

    def paintEvent(self, event):
        control = self._control
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        rect = QRectF(self.rect())

        if self.index > 0:
            separator = QPen(palette.color(QPalette.ColorRole.Mid))
            separator.setWidthF(1.0)
            painter.setPen(separator)
            painter.drawLine(QLineF(
                rect.left(),
                rect.top() + 6,
                rect.left(),
                rect.bottom() - 6,
            ))

        background = None
        border = None
        text_role = QPalette.ColorRole.ButtonText
        if not self.isEnabled() or not control.isEnabled():
            text_role = QPalette.ColorRole.PlaceholderText
            if self.isChecked():
                background = palette.color(QPalette.ColorRole.Window)
                border = palette.color(QPalette.ColorRole.Mid)
        elif self.isChecked():
            background = palette.color(QPalette.ColorRole.Button)
            border = palette.color(QPalette.ColorRole.Highlight)
        elif self.isDown():
            background = palette.color(QPalette.ColorRole.Mid)
        elif self.underMouse():
            background = palette.color(QPalette.ColorRole.AlternateBase)

        if background is not None:
            selected_rect = rect.adjusted(2, 2, -2, -2)
            painter.setBrush(background)
            painter.setPen(
                QPen(border, 1.0)
                if border is not None
                else Qt.PenStyle.NoPen
            )
            painter.drawPath(control._segment_path(selected_rect, self.index))

        painter.setPen(palette.color(text_role))
        painter.setFont(self.font())
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            self.text(),
        )


class SegmentedControl(QWidget):
    """Horizontal, exclusive selector with stable values and one tab stop."""

    valueChanged = pyqtSignal(object)
    currentIndexChanged = pyqtSignal(int)

    FRAME_INSET = 2
    FRAME_BORDER_WIDTH = 1.0
    FOCUS_BORDER_WIDTH = 2.0
    INNER_RADIUS = 4.0

    SIZE_METRICS = {
        SegmentedControlSize.SMALL: _SizeMetrics(
            minimum_height=30,
            horizontal_padding=10,
            vertical_padding=5,
            minimum_segment_width=64,
            font_size=Typography.SMALL,
        ),
        SegmentedControlSize.MEDIUM: _SizeMetrics(
            minimum_height=36,
            horizontal_padding=14,
            vertical_padding=7,
            minimum_segment_width=80,
            font_size=Typography.BODY,
        ),
        SegmentedControlSize.LARGE: _SizeMetrics(
            minimum_height=44,
            horizontal_padding=18,
            vertical_padding=9,
            minimum_segment_width=96,
            font_size=Typography.SUBTITLE,
        ),
    }
    RADIUS_VALUES = {
        SegmentedControlRadius.SMALL: 6.0,
        SegmentedControlRadius.MEDIUM: 8.0,
        SegmentedControlRadius.LARGE: 12.0,
    }

    def __init__(
        self,
        options=(),
        value=None,
        size=SegmentedControlSize.MEDIUM,
        radius=SegmentedControlRadius.LARGE,
        uniform=True,
        parent=None,
    ):
        super().__init__(parent)
        self._options = ()
        self._buttons = []
        self._current_index = -1
        self._focused_index = -1
        self._size = self._validate_size(size)
        self._radius = self._validate_radius(radius)
        self._uniform = bool(uniform)

        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(
            self.FRAME_INSET,
            self.FRAME_INSET,
            self.FRAME_INSET,
            self.FRAME_INSET,
        )
        self._layout.setSpacing(0)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setOptions(options)
        if value is not None:
            self.setValue(value)
        self._apply_metrics()

    def options(self):
        """Return an immutable snapshot of the configured options."""
        return self._options

    def setOptions(self, options):
        """Replace options, preserving the selected stable value when possible."""
        validated = self._validated_options(options)
        previous_value = self.value()
        previous_index = self._current_index

        self._clear_buttons()
        self._options = validated
        for index, option in enumerate(self._options):
            button = _SegmentButton(self, index, option)
            button.clicked.connect(
                lambda checked=False, item=index: self._activate_index(item)
            )
            self._button_group.addButton(button, index)
            self._layout.addWidget(button)
            self._buttons.append(button)

        retained_index = self._index_of_value(
            previous_value,
            require_enabled=True,
        )
        target_index = (
            retained_index
            if retained_index >= 0
            else self._first_enabled_index()
        )
        self._apply_current_index(target_index)
        self._apply_metrics()
        self._emit_changes(previous_value, previous_index)

    def value(self):
        """Return the selected stable value, or None when nothing is selectable."""
        if self._current_index < 0:
            return None
        return self._options[self._current_index].value

    def setValue(self, value):
        """Select an enabled option by stable value."""
        index = self._index_of_value(value)
        if index < 0:
            raise ValueError(f"Unknown segmented-control value: {value!r}")
        self.setCurrentIndex(index)

    def currentIndex(self):
        return self._current_index

    def setCurrentIndex(self, index):
        """Select an enabled option by index."""
        if not 0 <= index < len(self._options):
            raise IndexError(f"Segment index out of range: {index}")
        if not self._options[index].enabled:
            raise ValueError(f"Segment is disabled: {index}")
        previous_value = self.value()
        previous_index = self._current_index
        self._apply_current_index(index)
        self._emit_changes(previous_value, previous_index)

    def setOptionEnabled(self, index, enabled):
        """Enable or disable one option and keep selection valid."""
        if not 0 <= index < len(self._options):
            raise IndexError(f"Segment index out of range: {index}")
        enabled = bool(enabled)
        option = self._options[index]
        if option.enabled == enabled:
            return

        previous_value = self.value()
        previous_index = self._current_index
        updated = list(self._options)
        updated[index] = SegmentOption(option.value, option.label, enabled)
        self._options = tuple(updated)
        self._buttons[index].setEnabled(enabled)

        if index == self._current_index and not enabled:
            next_index = self._next_enabled_index(index, 1)
            if next_index < 0:
                next_index = self._next_enabled_index(index, -1)
            self._apply_current_index(next_index)
        elif self._current_index < 0 and enabled:
            self._apply_current_index(index)

        self._emit_changes(previous_value, previous_index)
        self.update()

    def optionEnabled(self, index):
        if not 0 <= index < len(self._options):
            raise IndexError(f"Segment index out of range: {index}")
        return self._options[index].enabled

    def controlSize(self):
        return self._size

    def setControlSize(self, size):
        size = self._validate_size(size)
        if size != self._size:
            self._size = size
            self._apply_metrics()

    def radius(self):
        return self._radius

    def setRadius(self, radius):
        radius = self._validate_radius(radius)
        if radius != self._radius:
            self._radius = radius
            self.update()
            for button in self._buttons:
                button.update()

    def uniformSegments(self):
        return self._uniform

    def setUniformSegments(self, uniform):
        uniform = bool(uniform)
        if uniform != self._uniform:
            self._uniform = uniform
            self._apply_metrics()

    def segmentButton(self, index):
        """Return a segment's native button for accessibility integration."""
        if not 0 <= index < len(self._buttons):
            raise IndexError(f"Segment index out of range: {index}")
        return self._buttons[index]

    def setAccessibleName(self, name):
        super().setAccessibleName(name)
        self._update_accessibility()

    def sizeHint(self):
        if not self._options:
            metrics = self.SIZE_METRICS[self._size]
            return QSize(0, metrics.minimum_height)
        hints = [self._segment_size_hint(index) for index in range(len(self._options))]
        if self._uniform:
            width = max(hint.width() for hint in hints) * len(hints)
        else:
            width = sum(hint.width() for hint in hints)
        height = max(hint.height() for hint in hints)
        return QSize(
            width + self.FRAME_INSET * 2,
            height + self.FRAME_INSET * 2,
        )

    def minimumSizeHint(self):
        return self.sizeHint()

    def changeEvent(self, event):
        if event.type() in {
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.PaletteChange,
            QEvent.Type.EnabledChange,
            QEvent.Type.FontChange,
        }:
            self._apply_metrics()
            self.update()
        super().changeEvent(event)

    def focusInEvent(self, event):
        if self._current_index >= 0:
            self._focused_index = self._current_index
        else:
            self._focused_index = self._first_enabled_index()
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.update()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            delta = -1 if key == Qt.Key.Key_Left else 1
            if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
                delta *= -1
            self._move_selection(delta)
            event.accept()
            return
        if key == Qt.Key.Key_Home:
            self._select_edge(first=True)
            event.accept()
            return
        if key == Qt.Key.Key_End:
            self._select_edge(first=False)
            event.accept()
            return
        if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._focused_index >= 0:
                self.setCurrentIndex(self._focused_index)
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        frame = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        radius = self._corner_radius(frame.height())

        painter.setBrush(
            palette.color(
                QPalette.ColorRole.AlternateBase
                if self.isEnabled()
                else QPalette.ColorRole.Window
            )
        )
        border = QPen(
            palette.color(
                QPalette.ColorRole.Highlight
                if self.hasFocus()
                else QPalette.ColorRole.Mid
            )
        )
        border.setWidthF(
            self.FOCUS_BORDER_WIDTH
            if self.hasFocus()
            else self.FRAME_BORDER_WIDTH
        )
        painter.setPen(border)
        painter.drawRoundedRect(frame, radius, radius)

    def _activate_index(self, index):
        if not self.isEnabled() or not self._options[index].enabled:
            return
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.setCurrentIndex(index)

    def _move_selection(self, delta):
        if not self._options:
            return
        start = (
            self._current_index
            if self._current_index >= 0
            else (-1 if delta > 0 else len(self._options))
        )
        index = self._next_enabled_index(start, delta)
        if index >= 0:
            self.setCurrentIndex(index)

    def _select_edge(self, first):
        indexes = (
            range(len(self._options))
            if first
            else range(len(self._options) - 1, -1, -1)
        )
        for index in indexes:
            if self._options[index].enabled:
                self.setCurrentIndex(index)
                return

    def _next_enabled_index(self, start, delta):
        index = start + delta
        while 0 <= index < len(self._options):
            if self._options[index].enabled:
                return index
            index += delta
        return -1

    def _first_enabled_index(self):
        for index, option in enumerate(self._options):
            if option.enabled:
                return index
        return -1

    def _index_of_value(self, value, require_enabled=False):
        for index, option in enumerate(self._options):
            if option.value == value and (option.enabled or not require_enabled):
                return index
        return -1

    def _apply_current_index(self, index):
        self._current_index = index
        self._focused_index = index
        if index < 0:
            self._button_group.setExclusive(False)
            for button in self._buttons:
                button.setChecked(False)
            self._button_group.setExclusive(True)
        else:
            self._buttons[index].setChecked(True)
        self._update_accessibility()
        self.update()

    def _emit_changes(self, previous_value, previous_index):
        if self._current_index != previous_index:
            self.currentIndexChanged.emit(self._current_index)
        if self.value() != previous_value:
            self.valueChanged.emit(self.value())

    def _update_accessibility(self):
        selected_label = ""
        for index, button in enumerate(self._buttons):
            button.setAccessibleName(self._options[index].label)
            button.setAccessibleDescription(self.accessibleName())
            button.update()
            if index == self._current_index:
                selected_label = self._options[index].label
        self.setAccessibleDescription(selected_label)

    def _clear_buttons(self):
        for button in self._buttons:
            self._button_group.removeButton(button)
            self._layout.removeWidget(button)
            button.setParent(None)
            button.deleteLater()
        self._buttons.clear()
        self._current_index = -1
        self._focused_index = -1

    def _validated_options(self, options):
        validated = tuple(options)
        values = []
        for option in validated:
            if not isinstance(option, SegmentOption):
                raise TypeError("options must contain SegmentOption instances")
            if option.value is None:
                raise ValueError("segment values cannot be None")
            if any(option.value == value for value in values):
                raise ValueError(
                    f"Duplicate segmented-control value: {option.value!r}"
                )
            values.append(option.value)
        return validated

    @staticmethod
    def _validate_size(size):
        if not isinstance(size, SegmentedControlSize):
            raise TypeError("size must be a SegmentedControlSize")
        return size

    @staticmethod
    def _validate_radius(radius):
        if not isinstance(radius, SegmentedControlRadius):
            raise TypeError("radius must be a SegmentedControlRadius")
        return radius

    def _apply_metrics(self):
        metrics = self.SIZE_METRICS[self._size]
        maximum_width = 0
        for index, button in enumerate(self._buttons):
            font = button.font()
            font.setPixelSize(metrics.font_size)
            font.setWeight(QFont.Weight.Medium)
            button.setFont(font)
            hint = self._segment_size_hint(index)
            button.setMinimumSize(hint)
            maximum_width = max(maximum_width, hint.width())

        if self._uniform:
            for button in self._buttons:
                button.setMinimumWidth(maximum_width)
                self._layout.setStretch(button.index, 1)
        else:
            for button in self._buttons:
                self._layout.setStretch(button.index, 0)

        self.setMinimumHeight(self.sizeHint().height())
        self.updateGeometry()
        self.update()

    def _segment_size_hint(self, index):
        metrics = self.SIZE_METRICS[self._size]
        if not 0 <= index < len(self._buttons):
            return QSize(
                metrics.minimum_segment_width,
                metrics.minimum_height,
            )
        button = self._buttons[index]
        font_metrics = button.fontMetrics()
        width = max(
            metrics.minimum_segment_width,
            font_metrics.horizontalAdvance(button.text())
            + metrics.horizontal_padding * 2,
        )
        height = max(
            metrics.minimum_height,
            font_metrics.height() + metrics.vertical_padding * 2,
        )
        return QSize(width, height)

    def _corner_radius(self, height):
        if self._radius == SegmentedControlRadius.FULL:
            return height / 2
        return min(self.RADIUS_VALUES[self._radius], height / 2)

    def _segment_path(self, rect, index):
        count = len(self._options)
        outer_radius = max(
            self.INNER_RADIUS,
            self._corner_radius(rect.height()) - 2,
        )
        left_radius = (
            outer_radius
            if index == 0
            else self.INNER_RADIUS
        )
        right_radius = (
            outer_radius
            if index == count - 1
            else self.INNER_RADIUS
        )
        return self._asymmetric_rounded_rect(
            rect,
            left_radius,
            right_radius,
        )

    @staticmethod
    def _asymmetric_rounded_rect(rect, left_radius, right_radius):
        left_radius = min(left_radius, rect.height() / 2, rect.width() / 2)
        right_radius = min(right_radius, rect.height() / 2, rect.width() / 2)
        path = QPainterPath()
        path.moveTo(rect.left() + left_radius, rect.top())
        path.lineTo(rect.right() - right_radius, rect.top())
        path.quadTo(
            rect.right(),
            rect.top(),
            rect.right(),
            rect.top() + right_radius,
        )
        path.lineTo(rect.right(), rect.bottom() - right_radius)
        path.quadTo(
            rect.right(),
            rect.bottom(),
            rect.right() - right_radius,
            rect.bottom(),
        )
        path.lineTo(rect.left() + left_radius, rect.bottom())
        path.quadTo(
            rect.left(),
            rect.bottom(),
            rect.left(),
            rect.bottom() - left_radius,
        )
        path.lineTo(rect.left(), rect.top() + left_radius)
        path.quadTo(
            rect.left(),
            rect.top(),
            rect.left() + left_radius,
            rect.top(),
        )
        path.closeSubpath()
        return path
