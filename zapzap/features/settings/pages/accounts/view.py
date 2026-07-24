"""View for the Accounts settings page."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from zapzap.features.settings.components import SettingsPage
from zapzap.ui.components import Button, Label


class AccountsSettingsView(SettingsPage):
    """Composable accounts settings view without account persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Accounts"),
            _("Manage your accounts and individual preferences."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_accounts_section()

    def _setup_accounts_section(self):
        self.accounts_section = QWidget(self)
        section_layout = QVBoxLayout(self.accounts_section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(8)

        header = QWidget(self.accounts_section)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title = Label(_("Account list"), "section_title", header)
        title.setObjectName("SettingsSectionTitle")
        self.btn_new_user = Button("+ " + _("Add account"), parent=header)
        self.btn_new_user.setAccessibleName(_("Add account"))
        header_layout.addWidget(title, 1)
        header_layout.addWidget(
            self.btn_new_user,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        section_layout.addWidget(header)

        description = Label(
            _("Each account can have independent settings."),
            "section_description",
            self.accounts_section,
        )
        description.setObjectName("SettingsSectionDescription")
        section_layout.addWidget(description)

        self.account_limit_label = Label(
            "", "section_description", self.accounts_section
        )
        self.account_limit_label.setObjectName("AccountsLimitLabel")
        self.account_limit_label.hide()
        section_layout.addWidget(self.account_limit_label)

        user_list = QWidget(self.accounts_section)
        self.user_list_layout = QVBoxLayout(user_list)
        self.user_list_layout.setContentsMargins(0, 4, 0, 0)
        self.user_list_layout.setSpacing(10)
        section_layout.addWidget(user_list)
        self.add_section(self.accounts_section)

    def add_user_card(self, card):
        self.user_list_layout.addWidget(card)

    def set_account_limit(self, count: int, limit: int):
        """Update account-limit feedback and the add action state."""
        limit_reached = count >= limit
        self.btn_new_user.setEnabled(not limit_reached)
        if limit_reached:
            self.account_limit_label.setText(
                _("Account limit of {limit} reached.").format(limit=limit)
            )
        else:
            self.account_limit_label.setText(
                _("{count} of {limit} accounts configured.").format(
                    count=count,
                    limit=limit,
                )
            )
        self.account_limit_label.setVisible(limit > 0)
