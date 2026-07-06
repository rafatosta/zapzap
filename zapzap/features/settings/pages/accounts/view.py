"""View for the Accounts settings page."""

from gettext import gettext as _

from zapzap.features.settings.components import (
    SettingsActionRow,
    SettingsCard,
    SettingsPage,
    SettingsSection,
)


class AccountsSettingsView(SettingsPage):
    """Composable accounts settings view without account persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Accounts"),
            _("Manage ZapZap accounts, notifications, icons, and User-Agent overrides."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_accounts_section()
        self._setup_add_account_section()

    def _setup_accounts_section(self):
        self.accounts_section = SettingsSection(
            _("Account list"),
            _("Each enabled account appears in the browser account list."),
        )
        self.accounts_card = SettingsCard()
        self.user_list_layout = self.accounts_card.layout
        self.user_list_layout.setSpacing(10)
        self.accounts_section.add_card(self.accounts_card)
        self.add_section(self.accounts_section)

    def _setup_add_account_section(self):
        add_section = SettingsSection(
            _("Add account"),
            _("Create another WhatsApp Web session."),
        )
        add_card = SettingsCard()
        add_row = SettingsActionRow(
            _("New account"),
            _("Add an account if the configured account limit allows it."),
            _("Add account"),
        )
        self.btn_new_user = add_row.button
        add_card.add_row(add_row)
        add_section.add_card(add_card)
        self.add_section(add_section)

    def add_user_card(self, card):
        self.user_list_layout.addWidget(card)
