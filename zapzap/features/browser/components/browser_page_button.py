"""Browser account page button component."""

from enum import Enum

from PyQt6.QtCore import QRectF, QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QColor,
    QIcon,
    QImage,
    QPainter,
    QPalette,
    QPixmap,
    qAlpha,
    qBlue,
    qGray,
    qGreen,
    qRed,
    qRgba,
)
from PyQt6.QtWidgets import QPushButton

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.accounts.domain.user import User


class AccountIndicatorState(Enum):
    """Account states the sidebar can determine without inference.

    Mapping:
    - ACTIVITY: enabled, unmuted account with unread messages
      -> theme activity teal;
    - NONE: no unread activity, muted notifications or disabled account
      -> no indicator.

    Web loading, connection errors and session validity are intentionally not
    represented because those states are not propagated to this component.
    Disabled accounts are represented by the grayscale avatar itself.
    """

    NONE = "none"
    ACTIVITY = "activity"


class BrowserPageButton(QPushButton):
    """Sidebar button that represents one user/account page."""

    BUTTON_SIZE = 48
    ICON_SIZE = 34
    BORDER_RADIUS = 12
    INDICATOR_RATIO = 0.23
    INDICATOR_BORDER_RATIO = 0.22
    INDICATOR_CARD_GAP_RATIO = 0.06
    MIN_INDICATOR_SIZE = 6.0
    MIN_INDICATOR_BORDER = 1.5
    MIN_INDICATOR_CARD_GAP = 2.0
    INACTIVE_AVATAR_GRAYSCALE = 1.0
    INACTIVE_AVATAR_OPACITY = 0.82

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
        self._card_background_role = QPalette.ColorRole.Window
        self._avatar_cache_key = None
        self._avatar_cache_icon = QIcon()

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

    @property
    def indicator_state(self):
        return self._resolve_indicator_state()

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
            self._card_background_role = QPalette.ColorRole.Highlight
            self.setStyleSheet(self.STYLE_PRESSED)
        elif self._is_selected:
            self._card_background_role = QPalette.ColorRole.AlternateBase
            self.setStyleSheet(self.STYLE_SELECTED)
        elif hovered:
            self._card_background_role = QPalette.ColorRole.AlternateBase
            self.setStyleSheet(self.STYLE_HOVER)
        else:
            self._card_background_role = QPalette.ColorRole.Window
            self.setStyleSheet(self.STYLE_NORMAL)
        self.update()

    def update_user_icon(self):
        """Refresh the user icon and tooltip from the current user state."""
        if self._user is None:
            self.setIcon(QIcon())
            self.setToolTip("")
            self.setAccessibleName("")
            self.setAccessibleDescription("")
            self.update()
            return

        # Quantitative data is deliberately not painted into the avatar.
        self.setIcon(self._account_avatar())
        tooltip = self._build_tooltip()
        self.setToolTip(tooltip)
        self.setAccessibleName(self._user.name or self.tr("Account"))
        self.setAccessibleDescription(self._build_accessible_description())
        self.update()

    def _resolve_indicator_state(self):
        if self._user is None:
            return AccountIndicatorState.NONE
        if not self._user.enable or not self._notifications_enabled():
            return AccountIndicatorState.NONE
        if self._number_notifications > 0:
            return AccountIndicatorState.ACTIVITY
        return AccountIndicatorState.NONE

    def _notifications_enabled(self):
        return bool(
            SettingsManager.get(f"{self._user.id}/notification", True)
        )

    def _account_avatar(self):
        """Return the current avatar with only account-state styling applied."""
        cache_key = (self._user.icon, bool(self._user.enable))
        if cache_key == self._avatar_cache_key:
            return self._avatar_cache_icon

        avatar = UserIcon.get_icon(self._user.icon)
        if not self._user.enable:
            avatar = self._inactive_avatar(avatar)

        self._avatar_cache_key = cache_key
        self._avatar_cache_icon = avatar
        return avatar

    @classmethod
    def _inactive_avatar(cls, avatar):
        """Apply the centralized inactive-account effect in memory."""
        sizes = avatar.availableSizes()
        source_size = (
            max(sizes, key=lambda size: size.width() * size.height())
            if sizes
            else QSize(UserIcon.PHOTO_SIZE, UserIcon.PHOTO_SIZE)
        )
        source = avatar.pixmap(source_size).toImage().convertToFormat(
            QImage.Format.Format_ARGB32
        )
        inactive = QImage(source.size(), QImage.Format.Format_ARGB32)
        inactive.fill(Qt.GlobalColor.transparent)

        grayscale = cls.INACTIVE_AVATAR_GRAYSCALE
        opacity = cls.INACTIVE_AVATAR_OPACITY
        for y in range(source.height()):
            for x in range(source.width()):
                pixel = source.pixel(x, y)
                gray = qGray(pixel)
                red = round(qRed(pixel) + (gray - qRed(pixel)) * grayscale)
                green = round(
                    qGreen(pixel) + (gray - qGreen(pixel)) * grayscale
                )
                blue = round(
                    qBlue(pixel) + (gray - qBlue(pixel)) * grayscale
                )
                alpha = round(qAlpha(pixel) * opacity)
                inactive.setPixel(x, y, qRgba(red, green, blue, alpha))

        return QIcon(QPixmap.fromImage(inactive))

    def indicator_rect(self):
        """Return the DPI-independent outer indicator geometry."""
        icon_size = min(self.iconSize().width(), self.iconSize().height())
        dot_size = max(
            self.MIN_INDICATOR_SIZE,
            icon_size * self.INDICATOR_RATIO,
        )
        border_width = max(
            self.MIN_INDICATOR_BORDER,
            dot_size * self.INDICATOR_BORDER_RATIO,
        )
        outer_size = dot_size + (2 * border_width)
        content = QRectF(self.contentsRect())
        card_gap = max(
            self.MIN_INDICATOR_CARD_GAP,
            min(content.width(), content.height())
            * self.INDICATOR_CARD_GAP_RATIO,
        )
        avatar = QRectF(
            content.center().x() - (icon_size / 2),
            content.center().y() - (icon_size / 2),
            icon_size,
            icon_size,
        )
        radius = outer_size / 2
        center_x = min(
            avatar.right(),
            content.right() - card_gap - radius,
        )
        center_y = max(
            avatar.top(),
            content.top() + card_gap + radius,
        )
        return QRectF(
            center_x - radius,
            center_y - radius,
            outer_size,
            outer_size,
        )

    def indicator_color(self):
        """Return the centralized color for the current real account state."""
        state = self.indicator_state
        if state == AccountIndicatorState.ACTIVITY:
            return QColor(ThemeManager.get_color("activity"))
        return QColor()

    def _indicator_border_color(self):
        return self.palette().color(self._card_background_role)

    def _build_accessible_description(self):
        descriptions = []
        if not self._user.enable:
            descriptions.append(self.tr("Account disabled"))
        elif self._number_notifications > 0:
            descriptions.append(
                self.tr("Unread messages: {}").format(
                    self._number_notifications
                )
            )
        if not self._notifications_enabled():
            descriptions.append(self.tr("Notifications muted"))
        return ". ".join(descriptions)

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
        """Update unread state without adding quantitative text to the avatar."""
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

    def paintEvent(self, event):
        """Paint a non-interactive status dot over the avatar."""
        super().paintEvent(event)
        if self.indicator_state == AccountIndicatorState.NONE:
            return

        outer_rect = self.indicator_rect()
        dot_size = max(
            self.MIN_INDICATOR_SIZE,
            min(self.iconSize().width(), self.iconSize().height())
            * self.INDICATOR_RATIO,
        )
        inner_rect = QRectF(
            outer_rect.center().x() - (dot_size / 2),
            outer_rect.center().y() - (dot_size / 2),
            dot_size,
            dot_size,
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._indicator_border_color())
        painter.drawEllipse(outer_rect)
        painter.setBrush(self.indicator_color())
        painter.drawEllipse(inner_rect)
        painter.end()
