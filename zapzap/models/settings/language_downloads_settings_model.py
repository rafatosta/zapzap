"""Model for the Idioma e downloads settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class LanguageDownloadsSettingsModel(ContextSettingsModel):
    """Model for Idioma e downloads settings state."""

    def __init__(self):
        super().__init__('language_downloads')
