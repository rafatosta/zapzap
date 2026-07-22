from gettext import gettext as _
from typing import Optional

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox

from zapzap.ui.components.button import Button
from zapzap.ui.components.check_box import CheckBox

from zapzap import LIMITE_USERS
from zapzap.core.config.settings_manager import SettingsManager


class AlertManager:
    """Centralizes translated and consistently styled application dialogs."""

    information_icon = QMessageBox.Icon.Information
    warning_icon = QMessageBox.Icon.Warning
    accept_role = QMessageBox.ButtonRole.AcceptRole
    action_role = QMessageBox.ButtonRole.ActionRole
    reject_role = QMessageBox.ButtonRole.RejectRole

    @classmethod
    def _message_box(
        cls,
        parent,
        title: str,
        message: str,
        icon: QMessageBox.Icon,
    ) -> QMessageBox:
        message_box = QMessageBox(parent)
        message_box.setIcon(icon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        return message_box

    @classmethod
    def _add_button(
        cls,
        message_box: QMessageBox,
        text: str,
        role: QMessageBox.ButtonRole,
    ) -> Button:
        button = Button(text, parent=message_box)
        button.setIcon(QIcon())
        message_box.addButton(button, role)
        return button

    @classmethod
    def _set_default_button(
        cls,
        message_box: QMessageBox,
        button: Button,
    ) -> None:
        message_box.setDefaultButton(button)
        button.setFocus()

    @classmethod
    def information(cls, parent, title: str, message: str):
        message_box = cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Information,
        )
        cls._set_default_button(
            message_box,
            cls._add_button(message_box, _("OK"), QMessageBox.ButtonRole.AcceptRole),
        )
        message_box.exec()

    @classmethod
    def warning(cls, parent, title: str, message: str):
        message_box = cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Warning,
        )
        cls._set_default_button(
            message_box,
            cls._add_button(message_box, _("OK"), QMessageBox.ButtonRole.AcceptRole),
        )
        message_box.exec()

    @classmethod
    def critical(cls, parent, title: str, message: str):
        message_box = cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Critical,
        )
        cls._set_default_button(
            message_box,
            cls._add_button(message_box, _("OK"), QMessageBox.ButtonRole.AcceptRole),
        )
        message_box.exec()

    @classmethod
    def action_dialog(
        cls,
        parent,
        title: str,
        message: str,
        informative_message: str,
        icon: QMessageBox.Icon,
        actions: tuple[tuple[str, str, QMessageBox.ButtonRole], ...],
        default_action: Optional[str] = None,
    ) -> Optional[str]:
        message_box = cls._message_box(parent, title, message, icon)
        message_box.setInformativeText(informative_message)

        buttons = {}
        for action_key, text, role in actions:
            buttons[action_key] = cls._add_button(message_box, text, role)

        if default_action is not None and default_action in buttons:
            cls._set_default_button(message_box, buttons[default_action])

        message_box.exec()
        clicked_button = message_box.clickedButton()
        for action_key, button in buttons.items():
            if clicked_button == button:
                return action_key
        return None

    @classmethod
    def critical_action(
        cls,
        parent,
        title: str,
        message: str,
        informative_message: str,
        action_text: str,
    ) -> bool:
        message_box = cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Critical,
        )
        message_box.setInformativeText(informative_message)
        ok_button = cls._add_button(
            message_box,
            _("OK"),
            QMessageBox.ButtonRole.AcceptRole,
        )
        action_button = cls._add_button(
            message_box,
            action_text,
            QMessageBox.ButtonRole.ActionRole,
        )
        cls._set_default_button(message_box, ok_button)
        message_box.exec()
        return message_box.clickedButton() == action_button

    @classmethod
    def question(cls, parent, title: str, message: str) -> bool:
        response, _ = cls.question_with_checkbox(parent, title, message)
        return response

    @classmethod
    def question_with_checkbox(
        cls,
        parent,
        title: str,
        message: str,
        checkbox_text: Optional[str] = None,
    ) -> tuple[bool, bool]:
        message_box = cls._message_box(
            parent,
            title,
            message,
            QMessageBox.Icon.Question,
        )
        yes_button = cls._add_button(
            message_box,
            _("Yes"),
            QMessageBox.ButtonRole.YesRole,
        )
        no_button = cls._add_button(
            message_box,
            _("No"),
            QMessageBox.ButtonRole.NoRole,
        )
        cls._set_default_button(message_box, no_button)

        checkbox = None
        if checkbox_text is not None:
            checkbox = CheckBox(checkbox_text)
            message_box.setCheckBox(checkbox)

        message_box.exec()
        return message_box.clickedButton() == yes_button, bool(
            checkbox is not None and checkbox.isChecked()
        )

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
