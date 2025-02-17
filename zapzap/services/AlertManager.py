from PyQt6.QtWidgets import QMessageBox

from zapzap import LIMITE_USERS
from gettext import gettext as _

from zapzap.services.SettingsManager import SettingsManager


class AlertManager:
    @staticmethod
    def information(parent, title: str, message: str):
        QMessageBox.information(parent, title, message)

    @staticmethod
    def warning(parent, title: str, message: str):
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def critical(parent, title: str, message: str):
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def question(parent, title: str, message: str) -> bool:
        response = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return response == QMessageBox.StandardButton.Yes

    @staticmethod
    def limit_users(parent):
        QMessageBox.information(
            parent, _("Information"), _("Limit of {} users reached.\nIt is not possible to create more users!").format(SettingsManager.get("users/size", LIMITE_USERS)))

    def no_active_account(parent):
        QMessageBox.information(
            parent, _("Attention"), _("No active account!"))
