"""Controller for the Accounts settings page."""

from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.components.card_user.card_user_controller import CardUserController
from zapzap.features.settings.pages.accounts.model import AccountsSettingsModel
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.settings.pages.accounts.view import AccountsSettingsView


class AccountsSettingsController(AccountsSettingsView):
    """Coordinates account settings state and account creation actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AccountsSettingsModel()
        self._load_users()
        self._connect_signals()
        self._update_account_limit()

    def _connect_signals(self):
        self.btn_new_user.clicked.connect(self._new_user)

    def _load_users(self):
        self.user_list = self.model.list_users()
        for user in self.user_list:
            self._add_user_card(user)

    def _add_user_card(self, user):
        card = CardUserController(user, on_deleted=self._account_deleted)
        self.add_user_card(card)

    def _new_user(self):
        new_user = self.model.create_user()
        if new_user:
            self.user_list.append(new_user)
            self._add_user_card(new_user)
            browser = self._get_browser()
            if browser:
                browser.add_new_user(new_user)
        else:
            AlertManager.limit_users(self)
        self._update_account_limit()

    def _account_deleted(self, user):
        self.user_list = [item for item in self.user_list if item.id != user.id]
        self._update_account_limit()

    def _update_account_limit(self):
        self.set_account_limit(
            self.model.account_count(),
            self.model.account_limit(),
        )

    @staticmethod
    def _get_browser():
        app = QApplication.instance()
        if not app:
            return None
        window = app.getWindow()
        return getattr(window, "browser", None) if window else None
