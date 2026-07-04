"""Model for the Sistema e inicialização settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class SystemStartupSettingsModel(ContextSettingsModel):
    """Model for Sistema e inicialização settings state."""

    def __init__(self):
        super().__init__('system_startup')
