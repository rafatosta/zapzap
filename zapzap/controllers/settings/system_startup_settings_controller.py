"""Controller for the Sistema e inicialização settings page."""

from zapzap.models.settings.system_startup_settings_model import SystemStartupSettingsModel
from zapzap.views.settings_pages.system_startup_settings_view import SystemStartupSettingsView


class SystemStartupSettingsController(SystemStartupSettingsView):
    """Coordinates Sistema e inicialização settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = SystemStartupSettingsModel()
