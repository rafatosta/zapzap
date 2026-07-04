"""Model for the Contas settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class AccountsSettingsModel(ContextSettingsModel):
    """Model for Contas settings state."""

    def __init__(self):
        super().__init__('accounts')
