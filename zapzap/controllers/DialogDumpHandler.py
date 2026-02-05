from pathlib import Path

from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QUrl

from gettext import gettext as _


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

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(_("Unexpected Error"))

        msg.setText(
            _("The application encountered an unexpected error.")
        )

        msg.setInformativeText(
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
            )
        )

        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        open_button = msg.addButton(
            _("Open folder"),
            QMessageBox.ButtonRole.ActionRole
        )

        msg.exec()

        if msg.clickedButton() == open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(zip_path)))
