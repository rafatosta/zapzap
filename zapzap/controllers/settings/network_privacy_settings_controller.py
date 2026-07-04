"""Controller for the Privacidade e rede settings page."""

from zapzap.models.settings.network_privacy_settings_model import NetworkPrivacySettingsModel
from zapzap.views.settings_pages.network_privacy_settings_view import NetworkPrivacySettingsView


class NetworkPrivacySettingsController(NetworkPrivacySettingsView):
    """Coordinates Privacidade e rede settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = NetworkPrivacySettingsModel()
