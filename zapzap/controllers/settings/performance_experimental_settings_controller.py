"""Controller for the Performance experimental settings page."""

from zapzap.models.settings.performance_experimental_settings_model import PerformanceExperimentalSettingsModel
from zapzap.views.settings_pages.performance_experimental_settings_view import PerformanceExperimentalSettingsView


class PerformanceExperimentalSettingsController(PerformanceExperimentalSettingsView):
    """Coordinates Performance experimental settings state and actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = PerformanceExperimentalSettingsModel()
