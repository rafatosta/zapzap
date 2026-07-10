"""Model for advanced customization settings state."""

from __future__ import annotations

from zapzap.core.config.settings.system import SystemSettings


class AdvancedCustomizationsSettingsModel():
    """Model for Customizações avançadas settings state."""

    def __init__(self) -> None:
        self._system_settings = SystemSettings()

    @property
    def dont_use_native_dialog(self) -> bool:
        """Whether file dialogs should avoid the native platform dialog."""
        return self._system_settings.dont_use_native_dialog
