"""Model for the Privacidade e rede settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class NetworkPrivacySettingsModel(ContextSettingsModel):
    """Model for Privacidade e rede settings state."""

    def __init__(self):
        super().__init__('network_privacy')
