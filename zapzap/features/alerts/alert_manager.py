from gettext import gettext as _
from typing import Optional

from PyQt6.QtWidgets import QLabel, QMessageBox, QSizePolicy

from zapzap import LIMITE_USERS
from zapzap.core.config.settings_manager import SettingsManager


class AlertManager:
    MESSAGE_MIN_WIDTH = 320
    MESSAGE_MAX_WIDTH = 560

    @classmethod
    def _message_box(
        cls,
        parent,
        title: str,
        message: str,
        icon: QMessageBox.Icon,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        default_button: Optional[QMessageBox.StandardButton] = None,
    ) -> QMessageBox:
        message_box = QMessageBox(parent)
        message_box.setIcon(icon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(buttons)

        if default_button is not None:
            message_box.setDefaultButton(default_button)

        cls._enable_message_wrapping(message_box)
        return message_box

    @classmethod
    def _enable_message_wrapping(cls, message_box: QMessageBox):
        message_box.setMinimumWidth(cls.MESSAGE_MIN_WIDTH)
        for label in message_box.findChildren(QLabel):
            label.setWordWrap(True)
            label.setMinimumWidth(cls.MESSAGE_MIN_WIDTH)
            label.setMaximumWidth(cls.MESSAGE_MAX_WIDTH)
            label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )

    @classmethod
    def information(cls, parent, title: str, message: str):
        cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Information,
        ).exec()

    @classmethod
    def warning(cls, parent, title: str, message: str):
        cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Warning,
        ).exec()

    @classmethod
    def critical(cls, parent, title: str, message: str):
        cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Critical,
        ).exec()

    @classmethod
    def question(cls, parent, title: str, message: str) -> bool:
        response = cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ).exec()
        return response == QMessageBox.StandardButton.Yes

    @classmethod
    def limit_users(cls, parent):
        cls.information(
            parent,
            _("Information"),
            _(
                "Limit of {} users reached.\n"
                "It is not possible to create more users!"
            ).format(SettingsManager.get("users/size", LIMITE_USERS)),
        )

    @classmethod
    def no_active_account(cls, parent):
        cls.information(parent, _("Attention"), _("No active account!"))
