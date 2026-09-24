"""Chrome-like protection for repeated WhatsApp downloads."""

from gettext import gettext as _

from PyQt6.QtWidgets import QMessageBox


class MultipleDownloadDecision:
    ALLOW_ONCE = "allow_once"
    ALWAYS_ALLOW = "always_allow"
    BLOCK = "block"


class MultipleDownloadDialog:
    """Ask before WhatsApp starts repeated downloads."""

    @staticmethod
    def ask(parent=None) -> str:
        message = QMessageBox(parent)
        message.setIcon(QMessageBox.Icon.Question)
        message.setWindowTitle(_("Multiple downloads"))
        message.setText(_("WhatsApp wants to download multiple files."))
        message.setInformativeText(
            _("Do you want to allow these additional downloads?")
        )

        allow_once = message.addButton(
            _("Allow once"),
            QMessageBox.ButtonRole.AcceptRole,
        )
        always_allow = message.addButton(
            _("Always allow"),
            QMessageBox.ButtonRole.YesRole,
        )
        block = message.addButton(
            _("Block"),
            QMessageBox.ButtonRole.RejectRole,
        )
        message.setDefaultButton(block)
        message.setEscapeButton(block)
        message.exec()

        clicked = message.clickedButton()
        if clicked is always_allow:
            return MultipleDownloadDecision.ALWAYS_ALLOW
        if clicked is allow_once:
            return MultipleDownloadDecision.ALLOW_ONCE
        return MultipleDownloadDecision.BLOCK
