"""Controller for the Idioma e downloads settings page."""

from zapzap.models.settings.language_downloads_settings_model import LanguageDownloadsSettingsModel
from zapzap.views.settings_pages.language_downloads_settings_view import LanguageDownloadsSettingsView


class LanguageDownloadsSettingsController(LanguageDownloadsSettingsView):
    """Coordinates Idioma e downloads settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = LanguageDownloadsSettingsModel()
