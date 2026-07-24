"""ZapZap-styled dialog for editing an account."""

from gettext import gettext as _

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QMenu, QVBoxLayout

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.ui.components import Button, ComboBox, Label, LineEdit


class EditAccountDialog(QDialog):
    """Edit an account name and icon using ZapZap UI components."""

    KEEP_ICON = "keep"
    REGENERATE_ICON = "regenerate"
    RESTORE_ICON = "restore"

    def __init__(
        self,
        current_name="",
        current_icon=None,
        user_agent_items=None,
        current_user_agent="Default",
        parent=None,
    ):
        super().__init__(parent)
        self._icon_action = self.KEEP_ICON
        self._staged_icon_svg = None
        self.setWindowTitle(_("Edit account"))
        self.setModal(True)
        self.setMinimumWidth(410)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._setup_ui(
            current_name,
            current_icon,
            user_agent_items or [],
            current_user_agent,
        )
        self._apply_style()

    def _setup_ui(
        self,
        current_name,
        current_icon,
        user_agent_items,
        current_user_agent,
    ):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(8)

        title = Label(_("Edit account"), "section_title", self)
        description = Label(
            _("Change the name and icon used to identify this account."),
            "description",
            self,
        )
        description.setWordWrap(True)

        field_label = Label(_("Account name"), "row_title", self)
        self.name_edit = LineEdit(current_name, self)
        self.name_edit.setAccessibleName(_("Account name"))
        self.name_edit.selectAll()

        icon_label = Label(_("Account icon"), "row_title", self)
        self.change_icon_button = Button(_("Change icon"), parent=self)
        self.change_icon_button.setIconSize(QSize(30, 30))
        if current_icon is not None:
            self.change_icon_button.setIcon(current_icon)

        icon_menu = QMenu(self.change_icon_button)
        regenerate_action = icon_menu.addAction(
            _("Generate new colors for the icon")
        )
        restore_action = icon_menu.addAction(_("Restore standard"))
        regenerate_action.triggered.connect(
            lambda: self._set_icon_action(self.REGENERATE_ICON)
        )
        restore_action.triggered.connect(
            lambda: self._set_icon_action(self.RESTORE_ICON)
        )
        self.change_icon_button.setMenu(icon_menu)

        self.icon_choice_label = Label(
            _("Keep current icon"), "description", self
        )

        advanced_label = Label(_("Advanced options"), "section_title", self)
        user_agent_label = Label(_("User-Agent"), "row_title", self)
        self.user_agent_selector = ComboBox(self)
        for user_agent in user_agent_items:
            display_name = _("Default") if user_agent == "Default" else user_agent
            self.user_agent_selector.addItem(display_name, user_agent)
        selected_index = self.user_agent_selector.findData(current_user_agent)
        if selected_index >= 0:
            self.user_agent_selector.setCurrentIndex(selected_index)
        user_agent_description = Label(
            _("Changes the identification used by this account when loading pages."),
            "description",
            self,
        )

        self.cancel_button = Button(_("Cancel"), parent=self)
        self.save_button = Button(_("Save"), parent=self)
        self.save_button.setDefault(True)
        self.save_button.setAutoDefault(True)

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 8, 0, 0)
        buttons.setSpacing(8)
        buttons.addStretch(1)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.save_button)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(8)
        layout.addWidget(field_label)
        layout.addWidget(self.name_edit)
        layout.addSpacing(8)
        layout.addWidget(icon_label)
        layout.addWidget(self.change_icon_button)
        layout.addWidget(self.icon_choice_label)
        layout.addSpacing(10)
        layout.addWidget(advanced_label)
        layout.addWidget(user_agent_label)
        layout.addWidget(self.user_agent_selector)
        layout.addWidget(user_agent_description)
        layout.addLayout(buttons)

        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)

    def _apply_style(self):
        self.setStyleSheet("""
            EditAccountDialog {
                background: palette(window);
                color: palette(text);
            }
        """)

    def _set_icon_action(self, action):
        self._icon_action = action
        if action == self.REGENERATE_ICON:
            self._staged_icon_svg = UserIcon.get_new_icon_svg()
            self.change_icon_button.setIcon(
                UserIcon.get_icon(self._staged_icon_svg)
            )
            self.icon_choice_label.setText(_("New icon colors selected."))
        elif action == self.RESTORE_ICON:
            self._staged_icon_svg = UserIcon.ICON_DEFAULT
            self.change_icon_button.setIcon(
                UserIcon.get_icon(self._staged_icon_svg)
            )
            self.icon_choice_label.setText(_("Standard icon selected."))

    def account_name(self):
        """Return the name currently entered in the dialog."""
        return self.name_edit.text()

    def icon_action(self):
        """Return the staged icon operation."""
        return self._icon_action

    def staged_icon_svg(self):
        """Return the previewed icon SVG, if the user selected a change."""
        return self._staged_icon_svg

    def user_agent(self):
        """Return the technical User-Agent value selected by the user."""
        return self.user_agent_selector.currentData()
