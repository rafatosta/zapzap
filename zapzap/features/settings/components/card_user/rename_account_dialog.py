"""ZapZap-styled dialog for renaming an account."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout

from zapzap.ui.components import Button, Label, LineEdit


class RenameAccountDialog(QDialog):
    """Collect an account name using ZapZap's reusable UI components."""

    def __init__(self, current_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Rename account"))
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._setup_ui(current_name)
        self._apply_style()

    def _setup_ui(self, current_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(8)

        title = Label(_("Rename account"), "section_title", self)
        description = Label(
            _("Choose a name to identify this account."),
            "description",
            self,
        )
        description.setWordWrap(True)

        field_label = Label(_("Account name"), "row_title", self)
        self.name_edit = LineEdit(current_name, self)
        self.name_edit.setAccessibleName(_("Account name"))
        self.name_edit.selectAll()

        self.cancel_button = Button(_("Cancel"), parent=self)
        self.rename_button = Button(_("Rename"), parent=self)
        self.rename_button.setDefault(True)
        self.rename_button.setAutoDefault(True)

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 8, 0, 0)
        buttons.setSpacing(8)
        buttons.addStretch(1)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.rename_button)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(8)
        layout.addWidget(field_label)
        layout.addWidget(self.name_edit)
        layout.addLayout(buttons)

        self.cancel_button.clicked.connect(self.reject)
        self.rename_button.clicked.connect(self.accept)

    def _apply_style(self):
        self.setStyleSheet("""
            RenameAccountDialog {
                background: palette(window);
                color: palette(text);
            }
        """)

    def account_name(self):
        """Return the name currently entered in the dialog."""
        return self.name_edit.text()

    @classmethod
    def get_name(cls, parent, current_name):
        """Run the modal dialog and return its value and acceptance state."""
        dialog = cls(current_name, parent)
        dialog.name_edit.setFocus()
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.account_name(), accepted
