"""Browser account page button component."""

from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from zapzap.models import User
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.SettingsManager import SettingsManager


class BrowserPageButton(QPushButton):
    """Sidebar button that represents one user/account page."""

    STYLE_NORMAL = """
    QPushButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 12px;
        qproperty-flat: true;
        qproperty-iconSize: 34px;
        padding: 0;
    }
    """

    STYLE_HOVER = """
    QPushButton {
        background-color: rgba(0, 168, 132, 0.12);
        border: 1px solid rgba(0, 168, 132, 0.24);
        border-radius: 12px;
        qproperty-flat: true;
        qproperty-iconSize: 34px;
        padding: 0;
    }
    """

    STYLE_SELECTED = """
    QPushButton {
        background-color: rgba(0, 168, 132, 0.18);
        border: 1px solid #00A884;
        border-radius: 12px;
        qproperty-flat: true;
        qproperty-iconSize: 34px;
        padding: 0;
    }
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
        self.setMinimumSize(QSize(48, 48))
        self.setMaximumSize(QSize(48, 48))
        self._apply_state_style()

    def _apply_state_style(self, hovered=False):
        if self._is_selected:
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
