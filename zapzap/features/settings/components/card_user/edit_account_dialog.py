"""ZapZap-styled dialog for editing an account."""

from gettext import gettext as _

from PyQt6.QtCore import QSignalBlocker, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMenu,
    QVBoxLayout,
)

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.system import SystemSettings
from zapzap.features.settings.components import SettingsRadioGroup
from zapzap.ui.components import (
    Button,
    ComboBox,
    Label,
    LineEdit,
    RadioButton,
)


class EditAccountDialog(QDialog):
    """Edit an account name and icon using ZapZap UI components."""

    KEEP_ICON = "keep"
    REGENERATE_ICON = "regenerate"
    RESTORE_ICON = "restore"
    USE_PHOTO = "photo"

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
        self._staged_icon_data = None
        self._current_icon_data = (
            current_icon
            if isinstance(current_icon, str) and current_icon
            else UserIcon.ICON_DEFAULT
        )
        self._staged_photo_data = UserIcon.photo(self._current_icon_data)
        current_default_icon = UserIcon.default_icon(self._current_icon_data)
        if UserIcon.is_photo(self._current_icon_data):
            self._staged_default_data = current_default_icon
            self._staged_default_action = self.RESTORE_ICON
        else:
            self._staged_default_data = current_default_icon
            self._staged_default_action = self.KEEP_ICON
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
        self.default_icon_radio = RadioButton(_("Default"), self)
        self.photo_radio = RadioButton(_("Photo"), self)
        self.image_type_group = SettingsRadioGroup(
            self.default_icon_radio,
            self.photo_radio,
            parent=self,
        )

        self.change_icon_button = Button(_("Change icon"), parent=self)
        self.change_icon_button.setIconSize(QSize(30, 30))
        if isinstance(current_icon, QIcon):
            self.change_icon_button.setIcon(current_icon)
        else:
            self.change_icon_button.setIcon(
                UserIcon.get_icon(self._current_icon_data)
            )

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

        self.choose_photo_button = Button(_("Choose photo"), parent=self)
        self.choose_photo_button.setIconSize(QSize(42, 42))
        self.choose_photo_button.setAccessibleName(_("Choose photo"))

        self.icon_choice_label = Label(
            _("Keep current icon"), "description", self
        )
        is_photo = UserIcon.is_photo(self._current_icon_data)
        self.photo_radio.setChecked(is_photo)
        self.default_icon_radio.setChecked(not is_photo)
        if is_photo:
            self.choose_photo_button.setIcon(
                UserIcon.get_icon(self._current_icon_data)
            )
            self.icon_choice_label.setText(_("Keep current icon"))
        self._update_image_controls()

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
        layout.addWidget(self.image_type_group)
        layout.addWidget(self.change_icon_button)
        layout.addWidget(self.choose_photo_button)
        layout.addWidget(self.icon_choice_label)
        layout.addSpacing(10)
        layout.addWidget(advanced_label)
        layout.addWidget(user_agent_label)
        layout.addWidget(self.user_agent_selector)
        layout.addWidget(user_agent_description)
        layout.addLayout(buttons)

        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)
        self.default_icon_radio.toggled.connect(
            self._handle_default_icon_selected
        )
        self.photo_radio.toggled.connect(self._handle_photo_selected)
        self.choose_photo_button.clicked.connect(self._choose_photo)

    def _apply_style(self):
        self.setStyleSheet("""
            EditAccountDialog {
                background: palette(window);
                color: palette(text);
            }
        """)

    def _set_icon_action(self, action):
        blocker = QSignalBlocker(self.default_icon_radio)
        self.default_icon_radio.setChecked(True)
        del blocker
        self._icon_action = action
        if action == self.REGENERATE_ICON:
            self._staged_default_data = UserIcon.get_new_icon_svg()
            self._staged_icon_data = self._persisted_default_image()
            self._staged_default_action = action
            self.change_icon_button.setIcon(
                UserIcon.get_icon(self._staged_default_data)
            )
            self.icon_choice_label.setText(_("New icon colors selected."))
        elif action == self.RESTORE_ICON:
            self._staged_default_data = UserIcon.ICON_DEFAULT
            self._staged_icon_data = self._persisted_default_image()
            self._staged_default_action = action
            self.change_icon_button.setIcon(
                UserIcon.get_icon(self._staged_default_data)
            )
            self.icon_choice_label.setText(_("Standard icon selected."))
        self._update_image_controls()

    def _handle_default_icon_selected(self, checked):
        if not checked:
            return
        self._icon_action = self._staged_default_action
        if self._icon_action == self.KEEP_ICON:
            self._staged_icon_data = None
        else:
            self._staged_icon_data = self._persisted_default_image()
        preview_data = self._staged_default_data
        self.change_icon_button.setIcon(UserIcon.get_icon(preview_data))
        self.icon_choice_label.setText(_("Standard icon selected."))
        self._update_image_controls()

    def _handle_photo_selected(self, checked):
        if not checked:
            return
        if self._staged_photo_data:
            self._stage_photo(self._staged_photo_data)
        else:
            self._choose_photo()

    def _choose_photo(self):
        options = QFileDialog.Option(0)
        if SystemSettings().dont_use_native_dialog:
            options = QFileDialog.Option.DontUseNativeDialog
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            _("Choose photo"),
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
            options=options,
        )
        if not file_path:
            if not (
                self._staged_photo_data
                or UserIcon.is_photo(self._current_icon_data)
            ):
                self.default_icon_radio.setChecked(True)
            return
        try:
            self._stage_photo(UserIcon.photo_from_file(file_path))
        except ValueError:
            if not UserIcon.is_photo(self._current_icon_data):
                self.default_icon_radio.setChecked(True)
            self.icon_choice_label.setText(_("Could not load preview image."))

    def _stage_photo(self, photo_data):
        self._staged_photo_data = photo_data
        self._staged_icon_data = UserIcon.persisted_image(
            self._staged_default_data,
            photo_data,
            use_photo=True,
        )
        self._icon_action = (
            self.KEEP_ICON
            if self._staged_icon_data == self._current_icon_data
            else self.USE_PHOTO
        )
        blocker = QSignalBlocker(self.photo_radio)
        self.photo_radio.setChecked(True)
        del blocker
        photo_icon = UserIcon.get_icon(photo_data)
        self.change_icon_button.setIcon(photo_icon)
        self.choose_photo_button.setIcon(photo_icon)
        self.icon_choice_label.setText(_("Preview image updated."))
        self._update_image_controls()

    def _persisted_default_image(self):
        return UserIcon.persisted_image(
            self._staged_default_data,
            self._staged_photo_data,
            use_photo=False,
        )

    def _update_image_controls(self):
        use_photo = self.photo_radio.isChecked()
        self.change_icon_button.setVisible(not use_photo)
        self.choose_photo_button.setVisible(use_photo)

    def account_name(self):
        """Return the name currently entered in the dialog."""
        return self.name_edit.text()

    def icon_action(self):
        """Return the staged icon operation."""
        return self._icon_action

    def staged_icon_svg(self):
        """Return the previewed persisted icon data for compatibility."""
        return self._staged_icon_data

    def staged_icon(self):
        """Return the previewed SVG or embedded photo."""
        return self._staged_icon_data

    def user_agent(self):
        """Return the technical User-Agent value selected by the user."""
        return self.user_agent_selector.currentData()
