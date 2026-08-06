"""Controller for the About settings page."""

from gettext import gettext as _

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.settings.pages.about.model import AboutSettingsModel
from zapzap.features.settings.pages.about.view import AboutSettingsView


class AboutSettingsController(AboutSettingsView):
    """Coordinates About metadata, links, dialogs, and clipboard actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AboutSettingsModel()
        self._copy_feedback_timer = QTimer(self)
        self._copy_feedback_timer.setSingleShot(True)
        self._copy_feedback_timer.timeout.connect(
            self._restore_copy_button_text
        )
        self._load_metadata()
        self._configure_signals()

    def _load_metadata(self):
        self.set_identity(self.model.app_name, self.model.version_text)
        self.set_technical_details(self.model.technical_details)

    def _configure_signals(self):
        links = self.model.project_links
        self.homepage_row.clicked.connect(
            lambda: self._open_project_link(links["website"])
        )
        self.issue_row.clicked.connect(
            lambda: self._open_project_link(links["bug_report"])
        )
        self.donate_row.clicked.connect(
            self._open_donations
        )
        self.license_row.clicked.connect(self._show_license)
        self.credits_row.clicked.connect(self._show_credits)
        self.copy_system_info_button.clicked.connect(self._copy_system_information)

    def _copy_system_information(self):
        QApplication.clipboard().setText(self.model.system_information)
        self.show_copy_feedback()
        self._copy_feedback_timer.start(2000)

    def _restore_copy_button_text(self):
        self.copy_system_info_button.setText(_("Copy system information"))

    def _show_license(self):
        AlertManager.information(
            self,
            _("License"),
            _(
                "ZapZap is free software licensed under {license_id} "
                "(GPL-3.0-or-later)."
            ).format(license_id=self.model.license_name),
        )

    def _show_credits(self):
        AlertManager.information(
            self,
            _("Credits and contributors"),
            _(
                "Created and maintained by {author}. Thanks to everyone who "
                "contributes translations, code, testing, and feedback."
            ).format(author=self.model.author_name),
        )

    @staticmethod
    def _open_project_link(url):
        QDesktopServices.openUrl(QUrl(url))

    @staticmethod
    def _open_donations():
        window = QApplication.instance().getWindow()
        return window.open_donations()
