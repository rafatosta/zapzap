

from zapzap.models.settings import AboutSettingsModel
from zapzap.views.settings import AboutSettingsView


class AboutSettingsController(AboutSettingsView):
    """Coordinates About page metadata and external link actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AboutSettingsModel()
        self._load_metadata()
        # self._configure_signals()

    def _load_metadata(self):
        self.set_identity(
            self.model.app_name,
            self.model.version_text,
            self.model.qt_version_text,
        )
        self.set_build_information(self.model.build_information)
        self.set_project_links(self.model.project_links)