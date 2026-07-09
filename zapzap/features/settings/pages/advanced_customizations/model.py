"""Model for advanced customization settings state."""

from __future__ import annotations

from zapzap.core.config.settings_manager import SettingsManager


class AdvancedCustomizationsSettingsModel():
    """Model for Customizações avançadas settings state."""

    _DONT_USE_NATIVE_DIALOG = ("system/DontUseNativeDialog", False)

    @property
    def dont_use_native_dialog(self) -> bool:
        """Whether file dialogs should avoid the native platform dialog."""
        key, default = self._DONT_USE_NATIVE_DIALOG
        return bool(SettingsManager.get(key, default))
