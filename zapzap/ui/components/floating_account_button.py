"""Floating compact account button shown when the browser sidebar is hidden."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QIcon
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

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.setGraphicsEffect(shadow)

        self.hide()

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
        """Anchor the button to the top-left corner of its parent widget."""
        self.move(self.MARGIN, self.MARGIN)
        self.raise_()
