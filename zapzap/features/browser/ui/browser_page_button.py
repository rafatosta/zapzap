"""Browser account page button component."""

from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from zapzap.models import User
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings_manager import SettingsManager


class BrowserPageButton(QPushButton):
    """Sidebar button that represents one user/account page."""

    BUTTON_SIZE = 48
    ICON_SIZE = 34
    BORDER_RADIUS = 12

    STYLE_NORMAL = f"""
    QPushButton {{
        min-width: {BUTTON_SIZE}px;
        min-height: {BUTTON_SIZE}px;
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: {BORDER_RADIUS}px;
        color: palette(button-text);
        qproperty-flat: true;
        qproperty-iconSize: {ICON_SIZE}px;
        padding: 0;
    }}
    QPushButton:disabled {{
        background-color: transparent;
        border-color: transparent;
        color: palette(placeholder-text);
    }}
    """

    STYLE_HOVER = f"""
    QPushButton {{
        min-width: {BUTTON_SIZE}px;
        min-height: {BUTTON_SIZE}px;
        background-color: palette(alternate-base);
        border: 1px solid palette(mid);
        border-radius: {BORDER_RADIUS}px;
        color: palette(button-text);
        qproperty-flat: true;
        qproperty-iconSize: {ICON_SIZE}px;
        padding: 0;
    }}
    """

    STYLE_SELECTED = f"""
    QPushButton {{
        min-width: {BUTTON_SIZE}px;
        min-height: {BUTTON_SIZE}px;
        background-color: palette(alternate-base);
        border: 1px solid palette(highlight);
        border-radius: {BORDER_RADIUS}px;
        color: palette(button-text);
        qproperty-flat: true;
        qproperty-iconSize: {ICON_SIZE}px;
        padding: 0;
    }}
    """

    STYLE_PRESSED = f"""
    QPushButton {{
        min-width: {BUTTON_SIZE}px;
        min-height: {BUTTON_SIZE}px;
        background-color: palette(highlight);
        border: 1px solid palette(highlight);
        border-radius: {BORDER_RADIUS}px;
        color: palette(highlighted-text);
        qproperty-flat: true;
        qproperty-iconSize: {ICON_SIZE}px;
        padding: 0;
    }}
    """

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)
        self._user = user
        self.page_index = page_index
        self._number_notifications = 0
        self._is_selected = False

        self._setup_ui()
        self.update_user_icon()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        self.update_user_icon()

    @property
    def number_notifications(self):
        return self._number_notifications

    @property
    def isSelected(self):
        return self._is_selected

    def _setup_ui(self):
        """Configure the page button visual defaults."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setMinimumSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.setMaximumSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self._apply_state_style()

    def _apply_state_style(self, hovered=False, pressed=False):
        if pressed:
            self.setStyleSheet(self.STYLE_PRESSED)
        elif self._is_selected:
            self.setStyleSheet(self.STYLE_SELECTED)
        elif hovered:
            self.setStyleSheet(self.STYLE_HOVER)
        else:
            self.setStyleSheet(self.STYLE_NORMAL)

    def update_user_icon(self):
        """Refresh the user icon and tooltip from the current user state."""
        if self._user is None:
            self.setIcon(QIcon())
            self.setToolTip("")
            return

        user_icon_type = UserIcon.Type.Default
        if not self._user.enable:
            user_icon_type = UserIcon.Type.Disable
        elif not SettingsManager.get(f"{self._user.id}/notification", True):
            user_icon_type = UserIcon.Type.Silence

        self.setIcon(
            UserIcon.get_icon(
                self._user.icon,
                user_icon_type,
                self._number_notifications,
            )
        )
        self.setToolTip(self._build_tooltip())

    def _build_tooltip(self):
        tooltip = (
            f"{self._user.name} ({self._number_notifications})"
            if self._number_notifications > 0
            else self._user.name
        )
        if not self._user.enable:
            disabled_message = self.tr(
                "Account disabled - click to activate or right-click to manage"
            )
            tooltip = f"{tooltip}\n{disabled_message}" if tooltip else disabled_message
        return tooltip

    def update_notifications(self, number_notifications):
        """Update the unread notifications badge count."""
        self._number_notifications = number_notifications
        self.update_user_icon()

    def selected(self):
        """Mark the button as selected."""
        self._is_selected = True
        self._apply_state_style()

    def unselected(self):
        """Mark the button as unselected."""
        self._is_selected = False
        self._apply_state_style()

    def enterEvent(self, event):
        """Apply hover style when the cursor enters the button."""
        self._apply_state_style(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restore the current state style when the cursor leaves the button."""
        self._apply_state_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Apply the pressed style while the pointer is down."""
        self._apply_state_style(pressed=True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Restore selected or hover style when the pointer is released."""
        is_hovered = self.rect().contains(event.position().toPoint())
        self._apply_state_style(hovered=is_hovered)
        super().mouseReleaseEvent(event)
