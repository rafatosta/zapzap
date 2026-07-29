"""View for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtCore import QSignalBlocker, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.settings.components.settings_card import SettingsCard
from zapzap.features.settings.components.settings_rows import (
    SettingsSegmentedRow,
    SettingsSwitchRow,
)
from zapzap.ui.components import (
    Button,
    Label,
    SegmentOption,
    SegmentedControlRadius,
    SegmentedControlSize,
)


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
