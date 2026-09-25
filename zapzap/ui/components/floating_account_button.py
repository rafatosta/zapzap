"""Floating compact account button shown when the browser sidebar is hidden."""

from PyQt6.QtCore import QEvent, QPoint, QSize, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QIcon
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QToolButton

from zapzap.assets.icons.user_icon import UserIcon


class FloatingAccountButton(QToolButton):
    """Compact overlay exposing the active account when the sidebar is off."""

    BUTTON_SIZE = 40
    ICON_SIZE = 24
    BORDER_RADIUS = 12
    MARGIN = 10

    STYLE = f"""
    QToolButton {{
        min-width: {BUTTON_SIZE}px;
        min-height: {BUTTON_SIZE}px;
        max-width: {BUTTON_SIZE}px;
        max-height: {BUTTON_SIZE}px;
        border: 1px solid palette(mid);
        border-radius: {BORDER_RADIUS}px;
        padding: 0;
        background-color: palette(window);
        qproperty-iconSize: {ICON_SIZE}px;
    }}
    QToolButton:hover {{
        background-color: palette(alternate-base);
        border-color: palette(highlight);
    }}
    QToolButton:pressed {{
        background-color: palette(highlight);
        border-color: palette(highlight);
    }}
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("floating_account_button")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setStyleSheet(self.STYLE)
        self._drag_start = None
        self._dragging = False
        self._position_initialized = False
        if parent is not None:
            parent.installEventFilter(self)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.setGraphicsEffect(shadow)

        self.hide()

    def eventFilter(self, watched, event):
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            self._clamp_position()
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
            self._dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        distance = 0
        if self._drag_start is not None:
            distance = (
                event.position().toPoint() - self._drag_start
            ).manhattanLength()
        if (
            self._drag_start is not None
            and event.buttons() & Qt.MouseButton.LeftButton
            and distance >= QGuiApplication.styleHints().startDragDistance()
        ):
            self._dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.move(self._clamped_position(
                self.pos() + event.position().toPoint() - self._drag_start
            ))
            self._position_initialized = True
            self.setDown(False)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        dragging = self._dragging
        self._drag_start = None
        self._dragging = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if dragging:
            self.setDown(False)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_account(self, user):
        """Reflect the given account's identity, or clear when none is active."""
        if user is None:
            self.setIcon(QIcon())
            self.setToolTip("")
            self.setAccessibleName("")
            return
        self.setIcon(UserIcon.get_icon(user.icon))
        name = user.name or self.tr("Account")
        self.setToolTip(name)
        self.setAccessibleName(name)

    def reposition(self):
        """Keep the button's position valid after its parent is resized."""
        if not self._position_initialized:
            self.move(self.MARGIN, self.MARGIN)
            self._position_initialized = True
        self._clamp_position()
        self.raise_()

    def _clamped_position(self, position):
        parent = self.parentWidget()
        if parent is None:
            return position
        return QPoint(
            max(0, min(position.x(), parent.width() - self.width())),
            max(0, min(position.y(), parent.height() - self.height())),
        )

    def _clamp_position(self):
        self.move(self._clamped_position(self.pos()))
