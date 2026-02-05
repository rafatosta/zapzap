from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QMessageBox
from pathlib import Path
from PyQt6.QtCore import QStandardPaths, Qt, QUrl


class DialogDumpHandler:

    ISSUE_URL = "https://github.com/rafatosta/zapzap/issues"
    SUPPORT_EMAIL = "rafa.ecomp@gmail.com"

    @staticmethod
    def show_dialog(zip_path: Path) -> None:

        folder_path = zip_path.parent
        folder_url = QUrl.fromLocalFile(str(folder_path))

        print(f"Showing crash dialog for dump at: {zip_path}")
        print(f"Folder URL: {folder_url.toString()}")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Erro inesperado")
        msg.setText(
            "O aplicativo encontrou um erro inesperado."
        )
        msg.setInformativeText(
            f"Um relatório de diagnóstico foi gerado automaticamente em:\n\n{zip_path}\n\n"
            "Por favor, envie esse arquivo para o suporte para que possamos investigar o problema.\n"
            f" - Issue tracker: {DialogDumpHandler.ISSUE_URL}\n"
            f" - Email: {DialogDumpHandler.SUPPORT_EMAIL}\n\n"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        open_button = msg.addButton(
            "Abrir pasta", QMessageBox.ButtonRole.ActionRole
        )

        msg.exec()

        if msg.clickedButton() == open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(zip_path)))
