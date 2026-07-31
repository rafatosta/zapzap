"""Frameless ZapZap dialog for transactionally editing an account."""

from gettext import gettext as _

from PyQt6.QtCore import QPoint, QSignalBlocker, QSize, Qt
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.system import SystemSettings
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.ui.primitives import (
    Button,
    CloseButton,
    ComboBox,
    Label,
    LineEdit,
    SegmentOption,
    SegmentedControl,
    SegmentedControlRadius,
    SegmentedControlSize,
)


class _EditAccountHeader(QFrame):
    """Custom title bar that delegates system movement to Qt when possible."""

    HEIGHT = 64

    def __init__(self, dialog, icon):
        super().__init__(dialog)
        self.dialog = dialog
        self._drag_offset = None
        self.setObjectName("EditAccountHeader")
        self.setFixedHeight(self.HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 0, 18, 0)
        layout.setSpacing(12)

        self.account_icon = QLabel(self)
        self.account_icon.setObjectName("EditAccountHeaderIcon")
        self.account_icon.setFixedSize(36, 36)
        self.account_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.account_icon.setPixmap(icon.pixmap(26, 26))
        self.account_icon.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.title_label = Label(_("Edit account"), "section_title", self)
        self.title_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.close_button = CloseButton(
            self,
            tooltip=_("Close"),
            circular=True,
        )
        layout.addWidget(self.account_icon)
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        layout.addWidget(self.close_button)

        self.close_button.clicked.connect(dialog.reject)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        handle = self.dialog.windowHandle()
        if handle is not None and handle.startSystemMove():
            self._drag_offset = None
        else:
            self._drag_offset = (
                event.globalPosition().toPoint()
                - self.dialog.frameGeometry().topLeft()
            )
        event.accept()

    def mouseMoveEvent(self, event):
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.dialog.move(
                event.globalPosition().toPoint() - self._drag_offset
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Keep a fixed dialog from inheriting title-bar maximize behavior."""
        event.accept()


class EditAccountDialog(QDialog):
    """Edit account presentation using staged values committed on acceptance."""

    KEEP_ICON = "keep"
    REGENERATE_ICON = "regenerate"
    RESTORE_ICON = "restore"
    USE_PHOTO = "photo"

    IMAGE_DEFAULT = "default"
    IMAGE_PHOTO = "photo"

    DIALOG_WIDTH = 760
    DIALOG_HEIGHT = 720
    OUTER_MARGIN = 14
    WINDOW_RADIUS = 18
    PREVIEW_SIZE = 80

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
        self._initial_name = current_name
        self._initial_user_agent = current_user_agent
        self._initial_photo_data = UserIcon.photo(self._current_icon_data)
        self._staged_photo_data = self._initial_photo_data
        current_default_icon = UserIcon.default_icon(self._current_icon_data)
        self._initial_default_data = current_default_icon
        self._staged_default_data = current_default_icon
        self._staged_default_action = (
            self.RESTORE_ICON
            if UserIcon.is_photo(self._current_icon_data)
            else self.KEEP_ICON
        )

        self.setObjectName("EditAccountDialog")
        self.setWindowTitle(_("Edit account"))
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(self.DIALOG_WIDTH, self.DIALOG_HEIGHT)

        preview_icon = (
            current_icon
            if isinstance(current_icon, QIcon)
            else UserIcon.get_icon(self._current_icon_data)
        )
        self._setup_ui(
            current_name,
            preview_icon,
            user_agent_items or [],
            current_user_agent,
        )
        self._apply_style()
        self._connect_signals()
        self._update_image_controls()
        self._validate_name()
        self._setup_tab_order()

    def _setup_ui(
        self,
        current_name,
        preview_icon,
        user_agent_items,
        current_user_agent,
    ):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            self.OUTER_MARGIN,
            self.OUTER_MARGIN,
            self.OUTER_MARGIN,
            self.OUTER_MARGIN,
        )
        outer.setSpacing(0)

        self.window_frame = QFrame(self)
        self.window_frame.setObjectName("EditAccountWindowFrame")
        outer.addWidget(self.window_frame)

        shadow = QGraphicsDropShadowEffect(self.window_frame)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.window_frame.setGraphicsEffect(shadow)

        root = QVBoxLayout(self.window_frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = _EditAccountHeader(self, preview_icon)
        self.close_button = self.header.close_button
        root.addWidget(self.header)
        root.addWidget(self._divider("EditAccountHeaderDivider"))

        self.body_scroll = QScrollArea(self.window_frame)
        self.body_scroll.setObjectName("EditAccountBodyScroll")
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.body_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.content = QWidget(self.body_scroll)
        self.content.setObjectName("EditAccountContent")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(36, 26, 36, 26)
        content_layout.setSpacing(0)

        description = Label(
            _("Change the name and icon used to identify this account."),
            "description",
            self.content,
        )
        description.setWordWrap(True)
        content_layout.addWidget(description)
        content_layout.addSpacing(22)

        field_label = Label(_("Account name"), "row_title", self.content)
        self.name_edit = LineEdit(current_name, self.content)
        self.name_edit.setAccessibleName(_("Account name"))
        self.name_edit.selectAll()
        self.name_error_label = Label("", "row_description", self.content)
        self.name_error_label.setObjectName("AccountNameValidationError")
        self.name_error_label.setAccessibleName(_("Account name error"))
        self.name_error_label.hide()
        content_layout.addWidget(field_label)
        content_layout.addSpacing(6)
        content_layout.addWidget(self.name_edit)
        content_layout.addWidget(self.name_error_label)
        content_layout.addSpacing(18)

        icon_label = Label(_("Account icon"), "row_title", self.content)
        content_layout.addWidget(icon_label)
        content_layout.addSpacing(8)

        image_value = (
            self.IMAGE_PHOTO
            if UserIcon.is_photo(self._current_icon_data)
            else self.IMAGE_DEFAULT
        )
        self.image_type_control = SegmentedControl(
            options=(
                SegmentOption(self.IMAGE_DEFAULT, _("Default")),
                SegmentOption(self.IMAGE_PHOTO, _("Photo")),
            ),
            value=image_value,
            size=SegmentedControlSize.MEDIUM,
            radius=SegmentedControlRadius.LARGE,
            uniform=True,
            parent=self.content,
        )
        self.image_type_control.setAccessibleName(_("Account icon"))
        self.image_type_control.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.image_type_group = self.image_type_control
        content_layout.addWidget(self.image_type_control)
        content_layout.addSpacing(14)

        self.preview_card = QFrame(self.content)
        self.preview_card.setObjectName("AccountIconPreviewCard")
        preview_layout = QHBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(16, 14, 16, 14)
        preview_layout.setSpacing(16)

        self.preview_avatar = QLabel(self.preview_card)
        self.preview_avatar.setObjectName("AccountIconPreviewAvatar")
        self.preview_avatar.setFixedSize(
            self.PREVIEW_SIZE,
            self.PREVIEW_SIZE,
        )
        self.preview_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_avatar.setAccessibleName(_("Current icon"))
        preview_layout.addWidget(self.preview_avatar)

        preview_details = QWidget(self.preview_card)
        details_layout = QVBoxLayout(preview_details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(6)
        current_icon_label = Label(
            _("Current icon"),
            "row_title",
            preview_details,
        )
        details_layout.addWidget(current_icon_label)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)

        self.change_icon_button = Button(
            _("Change icon"),
            parent=preview_details,
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

        self.choose_photo_button = Button(
            _("Choose photo"),
            parent=preview_details,
        )
        self.choose_photo_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogOpenButton
            )
        )
        self.choose_photo_button.setAccessibleName(_("Choose photo"))

        self.photo_action_divider = self._vertical_divider(
            "AccountPhotoActionDivider",
            preview_details,
        )
        self.keep_current_button = Button(
            _("Keep current icon"),
            parent=preview_details,
        )
        self.keep_current_button.setObjectName("KeepCurrentIconButton")

        actions.addWidget(self.change_icon_button)
        actions.addWidget(self.choose_photo_button)
        actions.addWidget(self.photo_action_divider)
        actions.addWidget(self.keep_current_button)
        actions.addStretch(1)
        details_layout.addLayout(actions)

        self.icon_choice_label = Label(
            _("Keep current icon"),
            "row_description",
            preview_details,
        )
        details_layout.addWidget(self.icon_choice_label)
        preview_layout.addWidget(preview_details, 1)
        content_layout.addWidget(self.preview_card)
        content_layout.addSpacing(22)

        content_layout.addWidget(self._divider("EditAccountSectionDivider"))
        content_layout.addSpacing(20)

        advanced_label = Label(
            _("Advanced options"),
            "section_title",
            self.content,
        )
        content_layout.addWidget(advanced_label)
        content_layout.addSpacing(16)

        user_agent_header = QWidget(self.content)
        user_agent_header_layout = QHBoxLayout(user_agent_header)
        user_agent_header_layout.setContentsMargins(0, 0, 0, 0)
        user_agent_header_layout.setSpacing(6)
        user_agent_label = Label(
            _("User-Agent"),
            "row_title",
            user_agent_header,
        )
        user_agent_info = QLabel("ⓘ", user_agent_header)
        user_agent_help = _(
            "Changes the identification used by this account when loading pages."
        )
        user_agent_info.setObjectName("UserAgentInfoIcon")
        user_agent_info.setToolTip(user_agent_help)
        user_agent_info.setAccessibleName(_("User-Agent information"))
        user_agent_info.setAccessibleDescription(user_agent_help)
        user_agent_header_layout.addWidget(user_agent_label)
        user_agent_header_layout.addWidget(user_agent_info)
        user_agent_header_layout.addStretch(1)
        content_layout.addWidget(user_agent_header)
        content_layout.addSpacing(6)

        self.user_agent_selector = ComboBox(self.content)
        self.user_agent_selector.setAccessibleName(_("User-Agent"))
        for user_agent in user_agent_items:
            display_name = (
                _("Default") if user_agent == "Default" else user_agent
            )
            self.user_agent_selector.addItem(display_name, user_agent)
        selected_index = self.user_agent_selector.findData(current_user_agent)
        if selected_index < 0 and current_user_agent:
            display_name = (
                _("Default")
                if current_user_agent == "Default"
                else current_user_agent
            )
            self.user_agent_selector.addItem(
                display_name,
                current_user_agent,
            )
            selected_index = self.user_agent_selector.count() - 1
        if selected_index >= 0:
            self.user_agent_selector.setCurrentIndex(selected_index)
        content_layout.addWidget(self.user_agent_selector)
        content_layout.addSpacing(6)

        user_agent_description = Label(
            user_agent_help,
            "description",
            self.content,
        )
        content_layout.addWidget(user_agent_description)
        content_layout.addStretch(1)

        self.body_scroll.setWidget(self.content)
        root.addWidget(self.body_scroll, 1)
        root.addWidget(self._divider("EditAccountFooterDivider"))

        self.footer = QFrame(self.window_frame)
        self.footer.setObjectName("EditAccountFooter")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(24, 14, 24, 14)
        footer_layout.setSpacing(10)

        self.cancel_button = Button(_("Cancel"), parent=self.footer)
        self.save_button = Button(
            _("Save"),
            variant=Button.PRIMARY,
            parent=self.footer,
        )
        self.cancel_button.setMinimumWidth(100)
        self.save_button.setMinimumWidth(112)
        self.save_button.setDefault(True)
        self.save_button.setAutoDefault(True)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.save_button)
        root.addWidget(self.footer)

        self._set_preview_icon(preview_icon)

    def _connect_signals(self):
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)
        self.image_type_control.valueChanged.connect(
            self._handle_image_type_changed
        )
        self.choose_photo_button.clicked.connect(self._choose_photo)
        self.keep_current_button.clicked.connect(self._restore_current_icon)
        self.name_edit.textChanged.connect(self._validate_name)

    def _setup_tab_order(self):
        QWidget.setTabOrder(self.close_button, self.name_edit)
        QWidget.setTabOrder(self.name_edit, self.image_type_control)
        QWidget.setTabOrder(
            self.image_type_control,
            self.change_icon_button,
        )
        QWidget.setTabOrder(
            self.change_icon_button,
            self.choose_photo_button,
        )
        QWidget.setTabOrder(
            self.choose_photo_button,
            self.keep_current_button,
        )
        QWidget.setTabOrder(
            self.keep_current_button,
            self.user_agent_selector,
        )
        QWidget.setTabOrder(
            self.user_agent_selector,
            self.cancel_button,
        )
        QWidget.setTabOrder(self.cancel_button, self.save_button)

    def _apply_style(self):
        self.setStyleSheet(f"""
            EditAccountDialog {{
                background: transparent;
                color: palette(text);
            }}
            QFrame#EditAccountWindowFrame {{
                background: palette(window);
                border: 1px solid palette(mid);
                border-radius: {self.WINDOW_RADIUS}px;
            }}
            QFrame#EditAccountHeader,
            QFrame#EditAccountFooter,
            QWidget#EditAccountContent {{
                background: transparent;
                border: 0;
            }}
            QLabel#EditAccountHeaderIcon {{
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 18px;
            }}
            QScrollArea#EditAccountBodyScroll,
            QScrollArea#EditAccountBodyScroll > QWidget > QWidget {{
                background: transparent;
                border: 0;
            }}
            QFrame#EditAccountHeaderDivider,
            QFrame#EditAccountFooterDivider,
            QFrame#EditAccountSectionDivider {{
                color: palette(mid);
                background: palette(mid);
                border: 0;
                max-height: 1px;
            }}
            QFrame#AccountIconPreviewCard {{
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }}
            QLabel#AccountIconPreviewAvatar {{
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 40px;
            }}
            QFrame#AccountPhotoActionDivider {{
                color: palette(mid);
                background: palette(mid);
                border: 0;
                max-width: 1px;
            }}
            QPushButton#KeepCurrentIconButton {{
                border: 1px solid transparent;
                background: transparent;
                color: palette(link);
            }}
            QPushButton#KeepCurrentIconButton:hover {{
                background: palette(alternate-base);
                border-color: palette(mid);
            }}
            QPushButton#KeepCurrentIconButton:focus {{
                border: 2px solid palette(highlight);
            }}
            QLabel#AccountNameValidationError {{
                color: palette(bright-text);
            }}
            QLabel#UserAgentInfoIcon {{
                color: palette(placeholder-text);
                font-weight: 600;
            }}
        """)

    @staticmethod
    def _divider(object_name):
        divider = QFrame()
        divider.setObjectName(object_name)
        divider.setFrameShape(QFrame.Shape.HLine)
        return divider

    @staticmethod
    def _vertical_divider(object_name, parent=None):
        divider = QFrame(parent)
        divider.setObjectName(object_name)
        divider.setFrameShape(QFrame.Shape.VLine)
        return divider

    def _set_image_type(self, value):
        with QSignalBlocker(self.image_type_control):
            self.image_type_control.setValue(value)

    def _handle_image_type_changed(self, value):
        if value == self.IMAGE_DEFAULT:
            self._handle_default_icon_selected()
            return
        self._handle_photo_selected()

    def _set_icon_action(self, action):
        self._set_image_type(self.IMAGE_DEFAULT)
        self._icon_action = action
        if action == self.REGENERATE_ICON:
            self._staged_default_data = UserIcon.get_new_icon_svg()
            self._staged_icon_data = self._persisted_default_image()
            self._staged_default_action = action
            self.icon_choice_label.setText(_("New icon colors selected."))
        elif action == self.RESTORE_ICON:
            self._staged_default_data = UserIcon.ICON_DEFAULT
            self._staged_icon_data = self._persisted_default_image()
            self._staged_default_action = action
            self.icon_choice_label.setText(_("Standard icon selected."))
        self._set_preview_icon(
            UserIcon.get_icon(self._staged_default_data)
        )
        self._update_image_controls()

    def _handle_default_icon_selected(self, preserve_feedback=False):
        self._icon_action = self._staged_default_action
        if self._icon_action == self.KEEP_ICON:
            self._staged_icon_data = None
        else:
            self._staged_icon_data = self._persisted_default_image()
        if not preserve_feedback:
            self.icon_choice_label.setText(_("Standard icon selected."))
        self._set_preview_icon(
            UserIcon.get_icon(self._staged_default_data)
        )
        self._update_image_controls()

    def _handle_photo_selected(self):
        if self._staged_photo_data:
            self._stage_photo(self._staged_photo_data)
            return
        if not self._choose_photo():
            self._set_image_type(self.IMAGE_DEFAULT)
            self._handle_default_icon_selected(preserve_feedback=True)

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
            return False
        try:
            self._stage_photo(UserIcon.photo_from_file(file_path))
        except ValueError:
            self.icon_choice_label.setText(
                _("Could not load preview image.")
            )
            return False
        return True

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
        self._set_image_type(self.IMAGE_PHOTO)
        self._set_preview_icon(UserIcon.get_icon(photo_data))
        self.icon_choice_label.setText(_("Preview image updated."))
        self._update_image_controls()

    def _restore_current_icon(self):
        self._staged_photo_data = self._initial_photo_data
        self._staged_default_data = self._initial_default_data
        self._staged_icon_data = None
        self._icon_action = self.KEEP_ICON
        self._staged_default_action = (
            self.RESTORE_ICON
            if UserIcon.is_photo(self._current_icon_data)
            else self.KEEP_ICON
        )
        value = (
            self.IMAGE_PHOTO
            if UserIcon.is_photo(self._current_icon_data)
            else self.IMAGE_DEFAULT
        )
        self._set_image_type(value)
        self._set_preview_icon(
            UserIcon.get_icon(self._current_icon_data)
        )
        self.icon_choice_label.setText(_("Keep current icon"))
        self._update_image_controls()

    def _persisted_default_image(self):
        return UserIcon.persisted_image(
            self._staged_default_data,
            self._staged_photo_data,
            use_photo=False,
        )

    def _update_image_controls(self):
        use_photo = self.image_type_control.value() == self.IMAGE_PHOTO
        self.change_icon_button.setVisible(not use_photo)
        self.choose_photo_button.setVisible(use_photo)
        self.photo_action_divider.setVisible(use_photo)
        self.keep_current_button.setVisible(use_photo)

    def _set_preview_icon(self, icon):
        if icon.isNull():
            icon = UserIcon.get_icon(UserIcon.ICON_DEFAULT)
        self.preview_avatar.setPixmap(
            icon.pixmap(self.PREVIEW_SIZE - 8, self.PREVIEW_SIZE - 8)
        )

    def _validate_name(self, *_args):
        valid = bool(self.name_edit.text().strip())
        self.name_error_label.setText(
            "" if valid else _("Account name is required.")
        )
        self.name_error_label.setVisible(not valid)
        self.save_button.setEnabled(valid)
        self.name_edit.setProperty("invalid", not valid)
        self.name_edit.setAccessibleDescription(
            "" if valid else self.name_error_label.text()
        )
        self.name_edit.style().unpolish(self.name_edit)
        self.name_edit.style().polish(self.name_edit)
        return valid

    def has_unsaved_changes(self):
        return any((
            self.name_edit.text() != self._initial_name,
            self.user_agent() != self._initial_user_agent,
            self._icon_action != self.KEEP_ICON,
            (
                self._staged_icon_data is not None
                and self._staged_icon_data != self._current_icon_data
            ),
        ))

    def accept(self):
        if not self._validate_name():
            self.name_edit.setFocus()
            return
        super().accept()

    def reject(self):
        if not self.has_unsaved_changes():
            super().reject()
            return
        action = AlertManager.action_dialog(
            self,
            _("Discard account changes?"),
            _("There are unsaved changes to this account."),
            _("Discarding them restores the values from before editing."),
            AlertManager.warning_icon,
            (
                (
                    "discard",
                    _("Discard"),
                    QMessageBox.ButtonRole.DestructiveRole,
                    Button.DANGER,
                ),
                (
                    "keep",
                    _("Keep editing"),
                    QMessageBox.ButtonRole.RejectRole,
                ),
            ),
            "keep",
        )
        if action == "discard":
            super().reject()

    def closeEvent(self, event):
        if self.has_unsaved_changes():
            event.ignore()
            self.reject()
            return
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def account_name(self):
        """Return the name exactly as entered after validation."""
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
