"""Controller for the Contas settings page."""

from zapzap.models.settings.accounts_settings_model import AccountsSettingsModel
from zapzap.views.settings_pages.accounts_settings_view import AccountsSettingsView


class AccountsSettingsController(AccountsSettingsView):
    """Coordinates Contas settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AccountsSettingsModel()
