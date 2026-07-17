
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap.features.settings.pages.about.model import AboutSettingsModel
from zapzap.features.settings.pages.about.view import AboutSettingsView


class AboutSettingsController(AboutSettingsView):
    """Coordinates About page metadata and external link actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AboutSettingsModel()
        self._load_metadata()
        self._configure_signals()

    def _load_metadata(self):
        self.set_identity(
            self.model.app_name,
            self.model.version_text,
            self.model.qt_version_text,
        )
        self.set_build_information(self.model.build_information)
        self.set_project_links(self.model.project_links)

    def _configure_signals(self):
        links = self.model.project_links
        self.btnLeanMore.clicked.connect(
            lambda: self._open_project_link(links["website"])
        )
        self.btnReportIssue.clicked.connect(
            lambda: self._open_project_link(links["bug_report"])
        )
        self.btnDonate.clicked.connect(
            lambda: self._open_project_link(links["donation"])
        )

    @staticmethod
    def _open_project_link(url):
        QDesktopServices.openUrl(QUrl(url))
