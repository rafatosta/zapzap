"""Model for the Customizações avançadas settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class AdvancedCustomizationsSettingsModel(ContextSettingsModel):
    """Model for Customizações avançadas settings state."""

    def __init__(self):
        super().__init__('advanced_customizations')
