"""Controller for the Accounts settings page."""

from PyQt6.QtWidgets import QApplication

from zapzap.controllers.CardUser import CardUser
from zapzap.models.settings.accounts_settings_model import AccountsSettingsModel
from zapzap.services.AlertManager import AlertManager
from zapzap.views.settings.accounts_settings_view import AccountsSettingsView


class AccountsSettingsController(AccountsSettingsView):
    """Coordinates account settings state and account creation actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AccountsSettingsModel()
        self._load_users()
        self._connect_signals()

    def _connect_signals(self):
        self.btn_new_user.clicked.connect(self._new_user)

    def _load_users(self):
        self.user_list = self.model.list_users()
        for user in self.user_list:
            self.add_user_card(CardUser(user))

    def _new_user(self):
        new_user = self.model.create_user()
        if new_user:
            self.add_user_card(CardUser(new_user))
            browser = self._get_browser()
            if browser:
                browser.add_new_user(new_user)
        else:
            AlertManager.limit_users(self)

    @staticmethod
    def _get_browser():
        app = QApplication.instance()
        if not app:
            return None
        window = app.getWindow()
        return getattr(window, "browser", None) if window else None
