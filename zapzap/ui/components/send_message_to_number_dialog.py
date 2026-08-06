"""Native dialog for opening a WhatsApp chat with an unsaved number."""

from __future__ import annotations

from functools import cmp_to_key
from gettext import gettext as _

from PyQt6.QtCore import (
    QCollator,
    QEvent,
    QLocale,
    QModelIndex,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QKeyEvent,
    QStandardItem,
    QStandardItemModel,
    QTextCursor,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from zapzap.features.browser.web.open_chat import (
    ChatTarget,
    ChatTargetErrorCode,
    ChatTargetValidationError,
    MAX_MESSAGE_LENGTH,
    REGION_CALLING_CODES,
    validate_chat_target,
)
from zapzap.ui.primitives import (
    Button,
    CloseButton,
    ComboBox,
    Label,
    LineEdit,
    TextEdit,
)


class SendMessageToNumberDialog(QDialog):
    """Collect and validate a chat target without performing navigation."""

    message_requested = pyqtSignal(str, str)

    DIALOG_WIDTH = 660
    DIALOG_HEIGHT = 600
    OUTER_MARGIN = 14
    WINDOW_RADIUS = 18
    COUNTRY_SEARCH_ROLE = int(Qt.ItemDataRole.UserRole) + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target = None
        self._number_touched = False
        self._updating_message = False

        self.setObjectName("SendMessageToNumberDialog")
        self.setWindowTitle(_("Send message to number"))
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(self.DIALOG_WIDTH, self.DIALOG_HEIGHT)

        self._setup_ui()
        self._populate_countries()
        self._connect_signals()
        self._apply_style()
        self._setup_tab_order()
        self._refresh_validation()

    @property
    def chat_target(self) -> ChatTarget | None:
        return self._target

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(
            self.OUTER_MARGIN,
            self.OUTER_MARGIN,
            self.OUTER_MARGIN,
            self.OUTER_MARGIN,
        )
        root.setSpacing(0)

        self.window_frame = QFrame(self)
        self.window_frame.setObjectName("SendMessageWindowFrame")
        root.addWidget(self.window_frame)

        shadow = QGraphicsDropShadowEffect(self.window_frame)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.window_frame.setGraphicsEffect(shadow)

        window_layout = QVBoxLayout(self.window_frame)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)

        header = QFrame(self.window_frame)
        header.setObjectName("SendMessageHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(26, 18, 18, 16)
        header_layout.setSpacing(14)
        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(4)
        self.title_label = Label(
            _("Send message to number"),
            "section_title",
            header,
        )
        self.description_label = Label(
            _("Chat with someone who is not in your contact list."),
            "section_description",
            header,
        )
        heading_layout.addWidget(self.title_label)
        heading_layout.addWidget(self.description_label)
        self.close_button = CloseButton(
            header,
            tooltip=_("Close"),
            circular=True,
        )
        header_layout.addLayout(heading_layout, 1)
        header_layout.addWidget(
            self.close_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )
        window_layout.addWidget(header)

        content = QWidget(self.window_frame)
        content.setObjectName("SendMessageContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(26, 16, 26, 18)
        content_layout.setSpacing(9)

        phone_grid = QGridLayout()
        phone_grid.setContentsMargins(0, 0, 0, 0)
        phone_grid.setHorizontalSpacing(12)
        phone_grid.setVerticalSpacing(7)
        phone_grid.setColumnStretch(0, 2)
        phone_grid.setColumnStretch(1, 3)
        self.country_label = Label(_("Country code"), "row_title", content)
        self.number_label = Label(_("Phone number"), "row_title", content)
        self.country_combo = ComboBox(content)
        self.country_combo.setEditable(True)
        self.country_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.country_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.country_combo.setMinimumContentsLength(16)
        self.country_combo.setAccessibleName(_("Country code"))
        self.country_combo.setAccessibleDescription(
            _("Search by country name, region code, or international prefix.")
        )
        self.country_combo.lineEdit().setClearButtonEnabled(True)

        self.number_edit = LineEdit(parent=content)
        self.number_edit.setPlaceholderText(_("Example: 11 99999-9999"))
        self.number_edit.setMaxLength(32)
        field_height = max(
            self.country_combo.sizeHint().height(),
            self.number_edit.sizeHint().height(),
        )
        self.country_combo.setFixedHeight(field_height)
        self.number_edit.setFixedHeight(field_height)
        self.number_edit.setAccessibleName(_("Phone number"))
        self.number_edit.setAccessibleDescription(
            _("Enter the national number without repeating the country code.")
        )
        self.country_label.setBuddy(self.country_combo)
        self.number_label.setBuddy(self.number_edit)
        phone_grid.addWidget(self.country_label, 0, 0)
        phone_grid.addWidget(self.number_label, 0, 1)
        phone_grid.addWidget(self.country_combo, 1, 0)
        phone_grid.addWidget(self.number_edit, 1, 1)
        content_layout.addLayout(phone_grid)

        self.number_hint = Label(
            _("Enter the national number without the country code."),
            "row_description",
            content,
        )
        content_layout.addWidget(self.number_hint)

        self.error_label = Label("", "row_description", content)
        self.error_label.setObjectName("SendMessageError")
        self.error_label.setAccessibleName(_("Phone number error"))
        self.error_label.hide()
        content_layout.addWidget(self.error_label)

        message_header = QHBoxLayout()
        self.message_label = Label(
            _("Optional message"),
            "row_title",
            content,
        )
        self.message_count = Label("0/500", "row_description", content)
        self.message_count.setAccessibleName(_("Message character count"))
        message_header.addWidget(self.message_label)
        message_header.addStretch(1)
        message_header.addWidget(self.message_count)
        content_layout.addLayout(message_header)

        self.message_edit = TextEdit(parent=content)
        self.message_edit.setPlaceholderText(_("Hello! How are you?"))
        self.message_edit.setFixedHeight(108)
        self.message_edit.setAcceptRichText(False)
        self.message_edit.setAccessibleName(_("Optional message"))
        self.message_edit.setAccessibleDescription(
            _("Type an initial message. Press Control+Enter to continue.")
        )
        self.message_label.setBuddy(self.message_edit)
        self.message_edit.installEventFilter(self)
        content_layout.addWidget(self.message_edit)

        message_hint = Label(
            _("Type a message to start the conversation."),
            "row_description",
            content,
        )
        content_layout.addWidget(message_hint)

        info_box = QFrame(content)
        info_box.setObjectName("SendMessageInfoBox")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(14, 11, 14, 11)
        info_layout.setSpacing(3)
        info_layout.addWidget(
            Label(_("Your privacy is protected"), "row_title", info_box)
        )
        info_layout.addWidget(
            Label(
                _("The message will be sent directly to the number provided."),
                "row_description",
                info_box,
            )
        )
        content_layout.addWidget(info_box)
        content_layout.addStretch(1)
        window_layout.addWidget(content, 1)

        footer = QFrame(self.window_frame)
        footer.setObjectName("SendMessageFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(22, 14, 22, 14)
        footer_layout.setSpacing(8)
        self.cancel_button = Button(_("Cancel"), parent=footer)
        self.send_button = Button(
            _("Send message"),
            Button.PRIMARY,
            footer,
        )
        self.cancel_button.setAccessibleName(_("Cancel"))
        self.send_button.setAccessibleName(_("Send message"))
        self.send_button.setDefault(True)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.send_button)
        window_layout.addWidget(footer)

    def _populate_countries(self):
        collator = QCollator()
        collator.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        options = []
        for region_code, calling_code in REGION_CALLING_CODES.items():
            country = QLocale.codeToCountry(region_code)
            locale = QLocale(QLocale.Language.AnyLanguage, country)
            native_name = locale.nativeCountryName()
            english_name = QLocale.countryToString(country)
            country_name = native_name or english_name or region_code
            display = f"{country_name} ({region_code})  +{calling_code}"
            search_text = " ".join(
                part
                for part in (
                    country_name,
                    english_name,
                    region_code,
                    f"+{calling_code}",
                )
                if part
            )
            options.append((display, region_code, calling_code, search_text))

        options.sort(key=cmp_to_key(lambda left, right: collator.compare(
            left[0], right[0]
        )))
        for display, region_code, calling_code, search_text in options:
            self.country_combo.addItem(display, calling_code)
            index = self.country_combo.count() - 1
            self.country_combo.setItemData(
                index,
                region_code,
                Qt.ItemDataRole.UserRole + 1,
            )
            self.country_combo.setItemData(
                index,
                search_text,
                Qt.ItemDataRole.ToolTipRole,
            )

        completion_model = QStandardItemModel(self.country_combo)
        for display, _region_code, _calling_code, search_text in options:
            item = QStandardItem(display)
            item.setData(search_text, self.COUNTRY_SEARCH_ROLE)
            completion_model.appendRow(item)
        self._country_completer = QCompleter(
            completion_model,
            self.country_combo,
        )
        self._country_completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._country_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._country_completer.setCompletionRole(self.COUNTRY_SEARCH_ROLE)
        self._country_completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self.country_combo.setCompleter(self._country_completer)
        self._country_completer.activated[QModelIndex].connect(
            lambda index: self._select_country_text(
                str(index.data(Qt.ItemDataRole.DisplayRole) or "")
            )
        )

        brazil_index = next(
            (
                index
                for index in range(self.country_combo.count())
                if self.country_combo.itemData(
                    index,
                    Qt.ItemDataRole.UserRole + 1,
                ) == "BR"
            ),
            0,
        )
        self.country_combo.setCurrentIndex(brazil_index)

    def _connect_signals(self):
        self.close_button.clicked.connect(self.reject)
        self.cancel_button.clicked.connect(self.reject)
        self.send_button.clicked.connect(self._submit)
        self.number_edit.textChanged.connect(self._on_number_changed)
        self.number_edit.returnPressed.connect(self._submit)
        self.country_combo.currentIndexChanged.connect(
            self._refresh_validation
        )
        self.country_combo.lineEdit().textEdited.connect(
            self._on_country_text_edited
        )
        self.country_combo.lineEdit().editingFinished.connect(
            self._resolve_country_text
        )
        self.message_edit.textChanged.connect(self._on_message_changed)

    def _select_country_text(self, text):
        index = self.country_combo.findText(text, Qt.MatchFlag.MatchExactly)
        if index >= 0:
            self.country_combo.setCurrentIndex(index)

    def _on_country_text_edited(self, text):
        index = self.country_combo.findText(text, Qt.MatchFlag.MatchExactly)
        if index != self.country_combo.currentIndex():
            self.country_combo.setCurrentIndex(-1)
            self.country_combo.setEditText(text)
        self._refresh_validation()

    def _resolve_country_text(self):
        index = self.country_combo.findText(
            self.country_combo.currentText(),
            Qt.MatchFlag.MatchExactly,
        )
        if index >= 0:
            self.country_combo.setCurrentIndex(index)
        self._refresh_validation()

    def _on_number_changed(self, text):
        self._number_touched = True
        self._refresh_validation()

    def _on_message_changed(self):
        if self._updating_message:
            return
        text = self.message_edit.toPlainText()
        if len(text) > MAX_MESSAGE_LENGTH:
            self._updating_message = True
            position = min(
                self.message_edit.textCursor().position(),
                MAX_MESSAGE_LENGTH,
            )
            self.message_edit.setPlainText(text[:MAX_MESSAGE_LENGTH])
            cursor = self.message_edit.textCursor()
            cursor.setPosition(position, QTextCursor.MoveMode.MoveAnchor)
            self.message_edit.setTextCursor(cursor)
            self._updating_message = False
            text = self.message_edit.toPlainText()
        self.message_count.setText(f"{len(text)}/{MAX_MESSAGE_LENGTH}")
        self.message_count.setAccessibleDescription(
            _("{count} of {maximum} characters used.").format(
                count=len(text),
                maximum=MAX_MESSAGE_LENGTH,
            )
        )

    def _selected_country_code(self) -> str:
        if self.country_combo.currentIndex() < 0:
            return ""
        return str(self.country_combo.currentData() or "")

    def _validated_target(self) -> ChatTarget:
        return validate_chat_target(
            self._selected_country_code(),
            self.number_edit.text(),
            self.message_edit.toPlainText(),
        )

    @staticmethod
    def _error_message(code: ChatTargetErrorCode) -> str:
        messages = {
            ChatTargetErrorCode.MISSING_COUNTRY: _("Select a country code."),
            ChatTargetErrorCode.EMPTY_NUMBER: _("Enter a phone number."),
            ChatTargetErrorCode.NUMBER_TOO_SHORT: _(
                "The phone number appears to be incomplete."
            ),
            ChatTargetErrorCode.NUMBER_TOO_LONG: _(
                "The phone number exceeds the international limit."
            ),
            ChatTargetErrorCode.DUPLICATED_COUNTRY_CODE: _(
                "Do not include the country code again in this field."
            ),
            ChatTargetErrorCode.MESSAGE_TOO_LONG: _(
                "The message can contain up to 500 characters."
            ),
        }
        return messages[code]

    def _refresh_validation(self):
        try:
            self._validated_target()
        except ChatTargetValidationError as error:
            self.send_button.setEnabled(False)
            should_show = self._number_touched or (
                error.code == ChatTargetErrorCode.MISSING_COUNTRY
            )
            if should_show:
                message = self._error_message(error.code)
                self.error_label.setText(message)
                self.error_label.setAccessibleDescription(message)
                self.error_label.show()
                self._set_invalid_state(error.code)
            else:
                self.error_label.hide()
                self._set_invalid_state(None)
            return False

        self.error_label.hide()
        self._set_invalid_state(None)
        self.send_button.setEnabled(True)
        return True

    def _set_invalid_state(self, code: ChatTargetErrorCode | None):
        country_invalid = code == ChatTargetErrorCode.MISSING_COUNTRY
        for widget, invalid in (
            (self.country_combo, country_invalid),
            (self.number_edit, code is not None and not country_invalid),
        ):
            widget.setProperty("invalid", invalid)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _submit(self):
        try:
            target = self._validated_target()
        except ChatTargetValidationError as error:
            self._number_touched = True
            self._refresh_validation()
            if error.code == ChatTargetErrorCode.MISSING_COUNTRY:
                self.country_combo.setFocus(Qt.FocusReason.OtherFocusReason)
            else:
                self.number_edit.setFocus(Qt.FocusReason.OtherFocusReason)
            return

        self._target = target
        self.message_requested.emit(target.normalized_phone, target.message)
        self.accept()

    def _setup_tab_order(self):
        self.setTabOrder(self.country_combo, self.number_edit)
        self.setTabOrder(self.number_edit, self.message_edit)
        self.setTabOrder(self.message_edit, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.send_button)
        self.setTabOrder(self.send_button, self.close_button)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog#SendMessageToNumberDialog {
                background: transparent;
                color: palette(text);
            }
            QFrame#SendMessageWindowFrame {
                background: palette(window);
                border: 1px solid palette(mid);
                border-radius: %dpx;
            }
            QFrame#SendMessageHeader,
            QFrame#SendMessageFooter,
            QWidget#SendMessageContent {
                background: transparent;
                border: 0;
            }
            QFrame#SendMessageInfoBox {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
            QComboBox[invalid="true"] {
                border: 1px solid palette(bright-text);
            }
            QLabel#SendMessageError {
                color: palette(bright-text);
            }
        """ % self.WINDOW_RADIUS)

    def showEvent(self, event):
        super().showEvent(event)
        parent = self.parentWidget()
        if parent is not None:
            self.move(
                parent.frameGeometry().center()
                - self.rect().center()
            )
        self.number_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def eventFilter(self, watched, event):
        if watched is self.message_edit and event.type() == QEvent.Type.KeyPress:
            key_event = event
            if (
                key_event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and key_event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                if self.send_button.isEnabled():
                    self._submit()
                key_event.accept()
                return True
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)
