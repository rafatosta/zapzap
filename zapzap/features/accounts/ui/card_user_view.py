"""View for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QHBoxLayout, QToolButton, QWidget

from zapzap.ui.components import Button, LineEdit
from zapzap.features.settings.components.settings_card import SettingsCard
from zapzap.features.settings.components.settings_rows import (
    SettingsSelectRow,
    SettingsSwitchRow,
)


class CardUserView(SettingsCard):
    """Visual account card without persistence or application side effects."""

    def __init__(self, user_agent_items=None, parent=None):
        super().__init__(parent)
        self._setup_ui(user_agent_items or [])

    def _setup_ui(self, user_agent_items):
        header = QWidget(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 8, 0, 8)
        header_layout.setSpacing(12)

        self.icon = QToolButton(header)
        self.icon.setAutoRaise(True)
        self.icon.setIconSize(QSize(42, 42))

        self.name = LineEdit(parent=header)
        self.name.setPlaceholderText(_("Account name"))

        self.delete = Button(_("Delete"), header)

        header_layout.addWidget(self.icon)
        header_layout.addWidget(self.name, 1)
        header_layout.addWidget(self.delete)
        self.add_row(header)

        self.disable_row = SettingsSwitchRow(
            _("Disable account"),
            _("Hide this account and prevent it from loading."),
        )
        self.silence_row = SettingsSwitchRow(
            _("Do not disturb"),
            _("Disable notifications for this account."),
        )
        self.disable = self.disable_row.checkbox
        self.silence = self.silence_row.checkbox
        self.add_row(self.disable_row)
        self.add_row(self.silence_row)

        self.ua_row = SettingsSelectRow(
            _("User-Agent"),
            _("Select User-Agent for this account."),
            user_agent_items,
        )
        self.ua_selector = self.ua_row.combo
        self.add_row(self.ua_row)

    def enable_default_user_icon_menu(self):
        self.delete.hide()
        self.icon.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def set_user_name(self, name: str):
        self.name.setText(name)

    def set_account_disabled(self, disabled: bool):
        self.disable.setChecked(disabled)

    def set_notifications_silenced(self, silenced: bool):
        self.silence.setChecked(silenced)

    def set_selected_user_agent(self, user_agent: str):
        self.ua_selector.setCurrentText(user_agent)

    def set_user_icon(self, icon):
        self.icon.setIcon(icon)
