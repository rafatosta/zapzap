from gettext import gettext as _

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from zapzap.controllers.CardUser import CardUser
from zapzap.models.User import User
from zapzap.services.AlertManager import AlertManager
from zapzap.views.settings_components import SettingsActionRow, SettingsCard, SettingsPage, SettingsSection


class PageAccount(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_users()
        self.btn_new_user.clicked.connect(self._new_user)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(_("Accounts"), _("Manage ZapZap accounts, notifications, icons, and User-Agent overrides."), self)
        layout.addWidget(self.page)

        self.accounts_section = SettingsSection(_("Account list"), _("Each enabled account appears in the browser account list."))
        self.accounts_card = SettingsCard()
        self.user_list_layout = self.accounts_card.layout
        self.accounts_section.add_card(self.accounts_card)
        self.page.add_section(self.accounts_section)

        add_section = SettingsSection(_("Add account"), _("Create another WhatsApp Web session."))
        add_card = SettingsCard()
        add_row = SettingsActionRow(_("New account"), _("Add an account if the configured account limit allows it."), _("Add account"))
        add_card.add_row(add_row)
        self.btn_new_user = add_row.button
        add_section.add_card(add_card)
        self.page.add_section(add_section)
        self.page.add_stretch()

    def _load_users(self):
        self.user_list = User.select()
        for user in self.user_list:
            self.user_list_layout.addWidget(CardUser(user))

    def _new_user(self):
        new_user = User.create_new_user()
        if new_user:
            self.user_list_layout.addWidget(CardUser(new_user))
            QApplication.instance().getWindow().browser.add_new_user(new_user)
        else:
            AlertManager.limit_users(self)
