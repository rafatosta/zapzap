from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from gettext import gettext as _

from zapzap.features.alerts.alert_manager import AlertManager


class DialogDumpHandler:

    ISSUE_URL = "https://github.com/rafatosta/zapzap/issues"
    SUPPORT_EMAIL = "rafa.ecomp@gmail.com"

    @staticmethod
    def show_dialog(zip_path: Path) -> None:
        folder_path = zip_path.parent
        folder_url = QUrl.fromLocalFile(str(folder_path))

        # Debug auxiliar (opcional)
        print(f"Showing crash dialog for dump at: {zip_path}")
        print(f"Folder URL: {folder_url.toString()}")

        open_folder = AlertManager.critical_action(
            None,
            _("Unexpected Error"),
            _("The application encountered an unexpected error."),
            _(
                "A diagnostic report was generated automatically at:\n\n"
                "{path}\n\n"
                "Please send this file to support so we can investigate the issue.\n\n"
                "Report channels:\n"
                " - Issue tracker: {issue_url}\n"
                " - Email: {email}"
            ).format(
                path=zip_path,
                issue_url=DialogDumpHandler.ISSUE_URL,
                email=DialogDumpHandler.SUPPORT_EMAIL,
            ),
            _("Open folder"),
        )

        if open_folder:
            QDesktopServices.openUrl(folder_url)
