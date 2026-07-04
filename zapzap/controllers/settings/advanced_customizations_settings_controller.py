"""Controller for the Customizações avançadas settings page."""

from zapzap.models.settings.advanced_customizations_settings_model import AdvancedCustomizationsSettingsModel
from zapzap.views.settings_pages.advanced_customizations_settings_view import AdvancedCustomizationsSettingsView


class AdvancedCustomizationsSettingsController(AdvancedCustomizationsSettingsView):
    """Coordinates Customizações avançadas settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AdvancedCustomizationsSettingsModel()
