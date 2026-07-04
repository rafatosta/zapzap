"""Controller for the Suporte settings page."""

from zapzap.models.settings.support_settings_model import SupportSettingsModel
from zapzap.views.settings_pages.support_settings_view import SupportSettingsView


class SupportSettingsController(SupportSettingsView):
    """Coordinates Suporte settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = SupportSettingsModel()
