"""View for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtCore import QRectF, QSignalBlocker, QSize, Qt
from PyQt6.QtGui import QPainter, QPalette
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from zapzap.features.settings.components.settings_card import SettingsCard
from zapzap.features.settings.components.settings_rows import (
    SettingsSegmentedRow,
    SettingsSwitchRow,
)
from zapzap.ui.components import (
    Label,
    SegmentOption,
    SegmentedControlRadius,
    SegmentedControlSize,
)


class AccountActionsButton(QToolButton):
    """Compact palette-aware button for an account's contextual actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolTip(_("Account actions"))
        self.setAccessibleName(_("Account actions"))

    def sizeHint(self):
        return QSize(34, 34)

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        palette = self.palette()
        button_rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        background = palette.color(QPalette.ColorRole.Button)
        border = palette.color(QPalette.ColorRole.Mid)
        if self.isDown():
            background = palette.color(QPalette.ColorRole.Mid)
        elif self.underMouse():
            background = palette.color(QPalette.ColorRole.AlternateBase)
            border = palette.color(QPalette.ColorRole.Highlight)

        border_pen = painter.pen()
        border_pen.setColor(
            palette.color(QPalette.ColorRole.Highlight)
            if self.hasFocus()
            else border
        )
        border_pen.setWidth(2 if self.hasFocus() else 1)
        painter.setBrush(background)
        painter.setPen(border_pen)
        painter.drawRoundedRect(button_rect, 10, 10)

        dot_color = palette.color(
            QPalette.ColorRole.ButtonText
            if self.isEnabled()
            else QPalette.ColorRole.PlaceholderText
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dot_color)
        center_x = self.rect().center().x()
        center_y = self.rect().center().y()
        for offset in (-6, 0, 6):
            painter.drawEllipse(
                QRectF(center_x - 1.75, center_y + offset - 1.75, 3.5, 3.5)
            )


class CardUserView(SettingsCard):
    """Visual account card without persistence or application side effects."""

    ACCOUNT_ENABLED = "enabled"
    ACCOUNT_DISABLED = "disabled"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        header = QWidget(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 4, 0, 4)
        header_layout.setSpacing(12)

        self.icon = QToolButton(header)
        self.icon.setAutoRaise(True)
        self.icon.setIconSize(QSize(38, 38))
        self.icon.setToolTip(_("Change icon"))
        self.icon.setAccessibleName(_("Change icon"))

        self.name = Label("", "section_title", header)
        self.name.setObjectName("AccountCardName")
        self.name.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        self.menu_button = AccountActionsButton(header)

        header_layout.addWidget(self.icon)
        header_layout.addWidget(self.name, 1)
        header_layout.addWidget(self.menu_button)
        self.add_row(header)

        self.account_state_row = SettingsSegmentedRow(
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
        self.add_row(self.silence_row)

    def set_user_name(self, name: str):
        self.name.setText(name or _("Unnamed account"))

    def set_account_enabled(self, enabled: bool):
        with QSignalBlocker(self.active):
            self.active.setValue(
                self.ACCOUNT_ENABLED if enabled else self.ACCOUNT_DISABLED
            )

    def set_notifications_silenced(self, silenced: bool):
        self.silence.setChecked(silenced)

    def set_user_icon(self, icon):
        self.icon.setIcon(icon)

    def set_account_menu(self, menu):
        self.menu_button.setMenu(menu)
