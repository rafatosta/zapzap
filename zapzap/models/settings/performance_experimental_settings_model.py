"""Model for the Performance experimental settings page."""

from __future__ import annotations

from zapzap.models.settings.context_settings_model import ContextSettingsModel


class PerformanceExperimentalSettingsModel(ContextSettingsModel):
    """Model for Performance experimental settings state."""

    def __init__(self):
        super().__init__('performance_experimental')
