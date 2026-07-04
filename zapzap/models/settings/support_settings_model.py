"""Model for the Suporte settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class SupportSettingsModel(ContextSettingsModel):
    """Model for Suporte settings state."""

    def __init__(self):
        super().__init__('support')
