"""Reusable account-card and account-menu views."""

from gettext import gettext as _

from PyQt6.QtCore import QEvent, QPoint, QSignalBlocker, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QIcon
from PyQt6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from zapzap.assets.icons.user_icon import UserIcon
from .settings_card import SettingsCard
from .settings_rows import (
    SettingsSegmentedRow,
    SettingsSwitchRow,
)
from zapzap.ui.primitives import (
    Button,
    Label,
    SegmentOption,
    SegmentedControlRadius,
    SegmentedControlSize,
    ToggleSwitch,
)
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.ui.typography import Typography


class _ElidedAccountName(Label):
    """Account name which keeps its complete value for tooltip and a11y."""

    def __init__(self, parent=None):
        super().__init__("", "section_title", parent)
        self._full_text = ""
        self.setMinimumWidth(80)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

    def setFullText(self, text):
        self._full_text = text
        self.setAccessibleName(text)
        self._update_elision()

    def fullText(self):
        return self._full_text

    def resizeEvent(self, event):
        self._update_elision()
        super().resizeEvent(event)

    def _update_elision(self):
        elided = self.fontMetrics().elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            max(0, self.width()),
        )
        super().setText(elided)
        self.setToolTip(self._full_text if elided != self._full_text else "")


class _ResponsiveAccountStateRow(SettingsSegmentedRow):
    """Keep translated state text readable at narrow card widths."""

    STACK_BREAKPOINT = 520

    def resizeEvent(self, event):
        stacked = event.size().width() < self.STACK_BREAKPOINT
        direction = (
            QBoxLayout.Direction.TopToBottom
            if stacked
            else QBoxLayout.Direction.LeftToRight
        )
        layout = self.layout()
        if layout.direction() != direction:
            layout.setDirection(direction)
            layout.setAlignment(
                self.segmented,
                Qt.AlignmentFlag.AlignRight
                if stacked
                else Qt.AlignmentFlag.AlignVCenter,
            )
            self.updateGeometry()
        super().resizeEvent(event)


class CardUserView(SettingsCard):
    """Visual account card without persistence or application side effects."""

    ACCOUNT_ENABLED = "enabled"
    ACCOUNT_DISABLED = "disabled"

    AVATAR_SIZE = 48
    INACTIVE_AVATAR_GRAYSCALE = 1.0
    INACTIVE_AVATAR_OPACITY = 0.82
    HEADER_STACK_BREAKPOINT = 520

    def __init__(self, parent=None):
        super().__init__(parent)
        self._account_name = ""
        self._account_enabled = True
        self._notifications_silenced = False
        self._base_icon = QIcon()
        self._remove_available = True
        self._actions_busy = False
        self._header_stacked = None
        self._setup_ui()

    def _setup_ui(self):
        self.header = QWidget(self)
        self.header_layout = QGridLayout(self.header)
        self.header_layout.setContentsMargins(0, 6, 0, 6)
        self.header_layout.setHorizontalSpacing(12)
        self.header_layout.setVerticalSpacing(10)

        identity = QWidget(self.header)
        identity_layout = QHBoxLayout(identity)
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(14)

        self.icon = QLabel(identity)
        self.icon.setObjectName("AccountCardAvatar")
        self.icon.setFixedSize(self.AVATAR_SIZE, self.AVATAR_SIZE)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.name = _ElidedAccountName(identity)
        self.name.setObjectName("AccountCardName")

        identity_layout.addWidget(self.icon)
        identity_layout.addWidget(self.name, 1)

        self.actions = QWidget(self.header)
        actions_layout = QHBoxLayout(self.actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        self.edit_button = Button(_("Edit"), parent=self.actions)
        self.edit_button.setToolTip(_("Edit account"))
        self.edit_button.setAccessibleName(_("Edit account"))

        self.remove_button = Button(
            _("Remove"),
            variant=Button.DANGER,
            parent=self.actions,
        )

        self.remove_button.setToolTip(_("Remove account"))
        self.remove_button.setAccessibleName(_("Remove account"))

        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.remove_button)
        self.header_layout.addWidget(identity, 0, 0)
        self.header_layout.addWidget(
            self.actions,
            0,
            1,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self.add_row(self.header)

        self.account_state_row = _ResponsiveAccountStateRow(
            _("Account status"),
            _(
                "Disabled accounts remain saved, but are not loaded "
                "and do not receive notifications."
            ),
            options=(
                SegmentOption(self.ACCOUNT_ENABLED, _("Enabled")),
                SegmentOption(self.ACCOUNT_DISABLED, _("Disabled")),
            ),
            value=self.ACCOUNT_ENABLED,
            size=SegmentedControlSize.MEDIUM,
            radius=SegmentedControlRadius.LARGE,
        )
        self.active = self.account_state_row.segmented
        self.add_row(self.account_state_row)

        self.silence_row = SettingsSwitchRow(
            _("Do not disturb"),
            _("Silences notifications for this account."),
        )
        self.silence = self.silence_row.checkbox
        self.silence.setAccessibleName(_("Do not disturb"))
        self.add_row(self.silence_row)

        QWidget.setTabOrder(self.edit_button, self.remove_button)
        QWidget.setTabOrder(self.remove_button, self.active)
        QWidget.setTabOrder(self.active, self.silence)
        self._update_header_layout()
        self._update_accessibility()

    def resizeEvent(self, event):
        self._update_header_layout(event.size().width())
        super().resizeEvent(event)

    def _update_header_layout(self, width=None):
        stacked = (
            (self.width() if width is None else width)
            < self.HEADER_STACK_BREAKPOINT
        )
        if stacked == self._header_stacked:
            return
        self.header_layout.removeWidget(self.actions)
        if stacked:
            self.header_layout.addWidget(
                self.actions,
                1,
                0,
                1,
                2,
                Qt.AlignmentFlag.AlignRight,
            )
        else:
            self.header_layout.addWidget(
                self.actions,
                0,
                1,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )
        self._header_stacked = stacked

    def set_user_name(self, name: str):
        self._account_name = name or _("Unnamed account")
        self.name.setFullText(self._account_name)
        self.icon.setAccessibleName(self._account_name)
        self._update_accessibility()

    def set_account_enabled(self, enabled: bool):
        self._account_enabled = bool(enabled)
        with QSignalBlocker(self.active):
            self.active.setValue(
                self.ACCOUNT_ENABLED if enabled else self.ACCOUNT_DISABLED
            )
        self.silence.setEnabled(self._account_enabled)
        unavailable = (
            ""
            if self._account_enabled
            else _("Unavailable while the account is disabled.")
        )
        self.silence.setToolTip(unavailable)
        self.silence.setAccessibleDescription(
            unavailable or self.silence_row.description_label.text()
        )
        self._refresh_avatar()
        self._update_accessibility()

    def set_notifications_silenced(self, silenced: bool):
        self._notifications_silenced = bool(silenced)
        self.silence.setChecked(silenced)
        self._update_accessibility()

    def set_user_icon(self, icon):
        self._base_icon = icon
        self._refresh_avatar()

    def _refresh_avatar(self):
        icon = self._base_icon
        if not self._account_enabled and not icon.isNull():
            icon = UserIcon.grayscale_icon(
                icon,
                intensity=self.INACTIVE_AVATAR_GRAYSCALE,
                opacity=self.INACTIVE_AVATAR_OPACITY,
            )
        self.icon.setPixmap(
            icon.pixmap(QSize(self.AVATAR_SIZE, self.AVATAR_SIZE))
        )

    def set_remove_available(self, available: bool):
        self._remove_available = bool(available)
        if available:
            explanation = _("Remove account")
        else:
            explanation = _("The default account cannot be removed.")
        self.remove_button.setToolTip(explanation)
        self.remove_button.setAccessibleDescription(explanation)
        self.remove_button.setEnabled(
            self._remove_available and not self._actions_busy
        )

    def set_actions_busy(self, busy: bool):
        self._actions_busy = bool(busy)
        self.edit_button.setEnabled(not busy)
        self.remove_button.setEnabled(
            self._remove_available and not busy
        )

    def _update_accessibility(self):
        name = self._account_name or _("Unnamed account")
        status = _("Enabled") if self._account_enabled else _("Disabled")
        notifications = (
            _("Enabled") if self._notifications_silenced else _("Disabled")
        )
        self.setAccessibleName(f"{_('Account')} {name}")
        self.setAccessibleDescription(
            f"{_('Account status')}: {status}. "
            f"{_('Do not disturb')}: {notifications}."
        )


class _AccountMenuAction(QPushButton):
    """Text-only action row used by the account context popup."""

    def __init__(self, text, parent=None, *, destructive=False):
        super().__init__(text, parent)
        self.setObjectName(
            "AccountMenuDangerAction"
            if destructive
            else "AccountMenuAction"
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setIcon(QIcon())
        font = self.font()
        font.setPixelSize(Typography.BODY)
        font.setWeight(
            QFont.Weight.Medium
            if destructive
            else QFont.Weight.Normal
        )
        self.setFont(font)


class _AccountMenuSwitchRow(QWidget):
    """Compact switch row whose complete surface toggles the control."""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setObjectName("AccountMenuSwitchRow")
        self.setMinimumHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 10, 6)
        layout.setSpacing(16)

        self.label = Label(text, "body", self)
        self.label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        self.switch = ToggleSwitch(parent=self)
        self.switch.setAccessibleName(text)
        self.setFocusProxy(self.switch)

        layout.addWidget(self.label, 1)
        layout.addWidget(
            self.switch,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

    def setControlEnabled(self, enabled, explanation=""):
        self.setEnabled(enabled)
        self.setToolTip(explanation)
        self.switch.setToolTip(explanation)
        self.switch.setAccessibleDescription(explanation)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if enabled
            else Qt.CursorShape.ArrowCursor
        )
        self.switch.setCursor(
            Qt.CursorShape.PointingHandCursor
            if enabled
            else Qt.CursorShape.ArrowCursor
        )

    def mouseReleaseEvent(self, event):
        switch_area = self.switch.geometry()
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.isEnabled()
            and self.rect().contains(event.position().toPoint())
            and not switch_area.contains(event.position().toPoint())
        ):
            self.switch.toggle()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class AccountContextMenu(QFrame):
    """Keyboard-accessible account popover for the browser sidebar."""

    edit_requested = pyqtSignal()
    notifications_silenced_changed = pyqtSignal(bool)
    account_disabled_changed = pyqtSignal(bool)
    remove_requested = pyqtSignal()

    MENU_WIDTH = 320
    SURFACE_RADIUS = 12
    SHADOW_MARGIN = 10
    AVATAR_SIZE = 42

    def __init__(self, user, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint,
        )
        self.user = user
        self._base_icon = UserIcon.get_icon(user.icon)
        self._account_enabled = bool(user.enable)

        self.setObjectName("AccountContextMenu")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(self.MENU_WIDTH)
        self._setup_ui()
        self._apply_style()
        self.set_account_enabled(self._account_enabled)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
        )
        outer.setSpacing(0)

        self.surface = QFrame(self)
        self.surface.setObjectName("AccountContextMenuSurface")
        outer.addWidget(self.surface)

        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.surface.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        self.header = QWidget(self.surface)
        self.header.setObjectName("AccountMenuHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(12)

        self.avatar = QLabel(self.header)
        self.avatar.setObjectName("AccountMenuAvatar")
        self.avatar.setFixedSize(self.AVATAR_SIZE, self.AVATAR_SIZE)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        identity = QWidget(self.header)
        identity_layout = QVBoxLayout(identity)
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(2)

        self.name_label = _ElidedAccountName(identity)
        self.name_label.setObjectName("AccountMenuName")
        self.name_label.setMinimumWidth(0)
        self.name_label.setFullText(
            self.user.name or _("Unnamed account")
        )
        self.state_label = Label("", "row_description", identity)
        self.state_label.setObjectName("AccountMenuState")

        identity_layout.addWidget(self.name_label)
        identity_layout.addWidget(self.state_label)
        header_layout.addWidget(self.avatar)
        header_layout.addWidget(identity, 1)
        layout.addWidget(self.header)

        layout.addWidget(self._divider("AccountMenuHeaderDivider"))

        self.edit_action = _AccountMenuAction(
            _("Edit account"),
            self.surface,
        )
        self.edit_action.setAccessibleName(_("Edit account"))
        layout.addWidget(self.edit_action)

        self.notifications_row = _AccountMenuSwitchRow(
            _("Do not disturb"),
            self.surface,
        )
        self.notifications_switch = self.notifications_row.switch
        layout.addWidget(self.notifications_row)

        self.disable_row = _AccountMenuSwitchRow(
            _("Disable account"),
            self.surface,
        )
        self.disable_switch = self.disable_row.switch
        layout.addWidget(self.disable_row)

        layout.addWidget(self._divider("AccountMenuDangerDivider"))

        self.remove_action = _AccountMenuAction(
            _("Remove account"),
            self.surface,
            destructive=True,
        )
        self.remove_action.setAccessibleName(_("Remove account"))
        self.remove_action.setAccessibleDescription(
            _("Destructive action: removes this account.")
        )
        layout.addWidget(self.remove_action)

        self.edit_action.clicked.connect(
            lambda: self._close_and_emit(self.edit_requested)
        )
        self.notifications_switch.toggled.connect(
            self.notifications_silenced_changed.emit
        )
        self.disable_switch.toggled.connect(
            self._handle_disabled_toggled
        )
        self.remove_action.clicked.connect(
            lambda: self._close_and_emit(self.remove_requested)
        )

        for control in self._controls():
            control.installEventFilter(self)

        QWidget.setTabOrder(self.edit_action, self.notifications_switch)
        QWidget.setTabOrder(
            self.notifications_switch,
            self.disable_switch,
        )
        QWidget.setTabOrder(self.disable_switch, self.remove_action)

    @staticmethod
    def _divider(object_name):
        divider = QFrame()
        divider.setObjectName(object_name)
        divider.setFrameShape(QFrame.Shape.HLine)
        return divider

    def _apply_style(self):
        danger = ThemeManager.get_color("danger")
        danger_hover = ThemeManager.get_color("danger_hover")
        self.setStyleSheet(f"""
            QFrame#AccountContextMenu {{
                background: transparent;
                border: 0;
            }}
            QFrame#AccountContextMenuSurface {{
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: {self.SURFACE_RADIUS}px;
            }}
            QWidget#AccountMenuHeader,
            QWidget#AccountMenuHeader > QWidget {{
                background: transparent;
                border: 0;
            }}
            QLabel#AccountMenuAvatar {{
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: {self.AVATAR_SIZE // 2}px;
            }}
            QFrame#AccountMenuHeaderDivider,
            QFrame#AccountMenuDangerDivider {{
                color: palette(mid);
                background: palette(mid);
                border: 0;
                max-height: 1px;
                margin: 5px 4px;
            }}
            QPushButton#AccountMenuAction,
            QPushButton#AccountMenuDangerAction {{
                min-height: 42px;
                background: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 0 12px;
                text-align: left;
                color: palette(text);
            }}
            QPushButton#AccountMenuAction:hover,
            QWidget#AccountMenuSwitchRow:hover {{
                background: palette(alternate-base);
                border-color: palette(mid);
            }}
            QPushButton#AccountMenuAction:pressed {{
                background: palette(mid);
                border-color: palette(highlight);
            }}
            QPushButton#AccountMenuAction:focus,
            QPushButton#AccountMenuDangerAction:focus {{
                border: 2px solid palette(highlight);
            }}
            QWidget#AccountMenuSwitchRow {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
            }}
            QWidget#AccountMenuSwitchRow:disabled {{
                background: transparent;
                border-color: transparent;
            }}
            QPushButton#AccountMenuDangerAction {{
                color: {danger};
            }}
            QPushButton#AccountMenuDangerAction:hover {{
                color: {danger_hover};
                background: palette(alternate-base);
                border-color: {danger};
            }}
            QPushButton#AccountMenuDangerAction:pressed {{
                color: palette(highlighted-text);
                background: {danger};
                border-color: {danger};
            }}
            QPushButton#AccountMenuDangerAction:disabled {{
                color: palette(placeholder-text);
                background: transparent;
                border-color: transparent;
            }}
        """)

    def _controls(self):
        return (
            self.edit_action,
            self.notifications_switch,
            self.disable_switch,
            self.remove_action,
        )

    def set_notifications_silenced(self, silenced):
        with QSignalBlocker(self.notifications_switch):
            self.notifications_switch.setChecked(bool(silenced))

    def set_remove_available(self, available):
        available = bool(available)
        explanation = (
            _("Destructive action: removes this account.")
            if available
            else _("The default account cannot be removed.")
        )
        self.remove_action.setEnabled(available)
        self.remove_action.setToolTip(explanation)
        self.remove_action.setAccessibleDescription(explanation)

    def set_account_enabled(self, enabled):
        self._account_enabled = bool(enabled)
        with QSignalBlocker(self.disable_switch):
            self.disable_switch.setChecked(not self._account_enabled)
        status = (
            _("Active account")
            if self._account_enabled
            else _("Disabled account")
        )
        self.state_label.setText(status)

        icon = self._base_icon
        if not self._account_enabled and not icon.isNull():
            icon = UserIcon.grayscale_icon(
                icon,
                intensity=CardUserView.INACTIVE_AVATAR_GRAYSCALE,
                opacity=CardUserView.INACTIVE_AVATAR_OPACITY,
            )
        self.avatar.setPixmap(
            icon.pixmap(QSize(self.AVATAR_SIZE, self.AVATAR_SIZE))
        )

        unavailable = (
            ""
            if self._account_enabled
            else _("Unavailable while the account is disabled.")
        )
        self.notifications_row.setControlEnabled(
            self._account_enabled,
            unavailable,
        )

        account_name = self.user.name or _("Unnamed account")
        accessible = (
            _("Account {name}, active.")
            if self._account_enabled
            else _("Account {name}, disabled.")
        ).format(name=account_name)
        self.header.setAccessibleName(accessible)
        self.header.setAccessibleDescription(status)
        self.avatar.setAccessibleName(accessible)

    def _handle_disabled_toggled(self, disabled):
        self.set_account_enabled(not disabled)
        self.account_disabled_changed.emit(disabled)

    def _close_and_emit(self, signal):
        self.close()
        signal.emit()

    def popup(self, global_position):
        self.adjustSize()
        screen = (
            QGuiApplication.screenAt(global_position)
            or QGuiApplication.primaryScreen()
        )
        target = QPoint(global_position)
        if screen is not None:
            available = screen.availableGeometry()
            target.setX(
                min(
                    max(target.x(), available.left()),
                    available.right() - self.width() + 1,
                )
            )
            target.setY(
                min(
                    max(target.y(), available.top()),
                    available.bottom() - self.height() + 1,
                )
            )
        self.move(target)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.PopupFocusReason)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        if event.key() in {Qt.Key.Key_Up, Qt.Key.Key_Down}:
            controls = [
                control
                for control in self._controls()
                if control.isEnabled()
            ]
            if controls:
                target = (
                    controls[-1]
                    if event.key() == Qt.Key.Key_Up
                    else controls[0]
                )
                target.setFocus(Qt.FocusReason.ShortcutFocusReason)
            event.accept()
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched, event):
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)

        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return True
        if (
            event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}
            and isinstance(watched, QPushButton)
        ):
            watched.click()
            return True
        if event.key() not in {Qt.Key.Key_Up, Qt.Key.Key_Down}:
            return super().eventFilter(watched, event)

        controls = [control for control in self._controls() if control.isEnabled()]
        if not controls:
            return True
        current = watched if watched in controls else controls[0]
        index = controls.index(current)
        direction = -1 if event.key() == Qt.Key.Key_Up else 1
        controls[(index + direction) % len(controls)].setFocus(
            Qt.FocusReason.ShortcutFocusReason
        )
        return True
