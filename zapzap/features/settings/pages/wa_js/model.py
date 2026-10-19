"""Model for WA-JS settings."""
from zapzap.core.config.settings.wa_js import WaJsSettings

class WaJsSettingsModel:
    def __init__(self):
        self._settings = WaJsSettings()
    @property
    def enabled(self) -> bool:
        return self._settings.enabled
    @enabled.setter
    def enabled(self, value: bool):
        self._settings.enabled = bool(value)
