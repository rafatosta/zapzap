"""Reusable transactional dialog for choosing spellcheck languages."""

from __future__ import annotations

from gettext import gettext as _
import unicodedata

from PyQt6.QtCore import QLocale, QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLayout,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from zapzap.ui.primitives import Button, CloseButton, Label, LineEdit


class _FlowLayout(QLayout):
    """Small wrapping layout used by selected and recent language chips."""

    def __init__(self, parent=None, spacing=8):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._arrange(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._arrange(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        return size + QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom(),
        )

    def _arrange(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + spacing
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y += line_height + spacing
                next_x = x + hint.width() + spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y()


class SpellcheckLanguagePickerDialog(QDialog):
    """Palette-aware language picker whose changes remain staged until Apply."""

    CODE_ROLE = int(Qt.ItemDataRole.UserRole)
    SEARCH_ROLE = CODE_ROLE + 1

    def __init__(
        self,
        options,
        selected,
        recent=(),
        parent=None,
        *,
        maximum_selected,
        maximum_recent,
    ):
        super().__init__(parent)
        self.options = tuple(options)
        self._option_by_code = {option.code: option for option in self.options}
        self._original_selected = tuple(
            code for code in selected if code in self._option_by_code
        )
        self._selected = list(self._original_selected)
        self._recent = tuple(code for code in recent if code in self._option_by_code)
        self.maximum_selected = maximum_selected
        self.maximum_recent = maximum_recent
        self._updating_list = False
        self._letter_items = []
        self._language_items = {}

        self.setObjectName("SpellcheckLanguagePickerDialog")
        self.setWindowTitle(_("Languages"))
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self._setup_ui()
        self._apply_style()
        self._populate_languages()
        self._refresh_selection()
        self._fit_to_screen()
        self._setup_tab_order()

    @property
    def selected_languages(self) -> list[str]:
        return list(self._selected)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = QFrame(self)
        self.header.setObjectName("SpellcheckPickerHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(22, 16, 18, 16)
        self.title_label = Label(_("Languages"), "section_title", self.header)
        self.close_button = CloseButton(self.header, tooltip=_("Close"), circular=True)
        self.close_button.clicked.connect(self.reject)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.close_button)
        root.addWidget(self.header)

        content = QWidget(self)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(26, 18, 26, 18)
        content_layout.setSpacing(10)

        self.search_edit = LineEdit(parent=content)
        self.search_edit.setPlaceholderText(_("Search language"))
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setAccessibleName(_("Search language"))
        self.search_edit.setAccessibleDescription(
            _("Filter languages by name or dictionary code.")
        )
        self.search_edit.textChanged.connect(self._filter_languages)
        content_layout.addWidget(self.search_edit)

        selected_header = QHBoxLayout()
        selected_header.setContentsMargins(0, 4, 0, 0)
        selected_header.addWidget(Label(_("Selected languages"), "row_title", content))
        selected_header.addStretch(1)
        self.selected_count_label = Label("", "muted", content)
        selected_header.addWidget(self.selected_count_label)
        content_layout.addLayout(selected_header)
        selected_description = Label(
            _("They will be used for spell checking."),
            "row_description",
            content,
        )
        content_layout.addWidget(selected_description)

        self.selected_container = QWidget(content)
        self.selected_layout = _FlowLayout(self.selected_container)
        self.selected_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        content_layout.addWidget(self.selected_container)

        self.feedback_label = Label("", "row_description", content)
        self.feedback_label.setObjectName("SpellcheckPickerFeedback")
        self.feedback_label.setAccessibleName(_("Language selection status"))
        self.feedback_label.hide()
        content_layout.addWidget(self.feedback_label)

        self.recent_section = QWidget(content)
        recent_layout = QVBoxLayout(self.recent_section)
        recent_layout.setContentsMargins(0, 2, 0, 0)
        recent_layout.setSpacing(6)
        recent_layout.addWidget(Label(_("Recent"), "row_title", self.recent_section))
        self.recent_container = QWidget(self.recent_section)
        self.recent_layout = _FlowLayout(self.recent_container)
        recent_layout.addWidget(self.recent_container)
        content_layout.addWidget(self.recent_section)

        self.all_languages_label = Label(_("All languages"), "row_title", content)
        content_layout.addWidget(self.all_languages_label)
        self.language_list = QListWidget(content)
        self.language_list.setObjectName("SpellcheckLanguageList")
        self.language_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.language_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.language_list.setAccessibleName(_("All languages"))
        self.language_list.setAccessibleDescription(
            _("Use Space to select or remove the focused language.")
        )
        self.language_list.itemChanged.connect(self._on_item_changed)
        content_layout.addWidget(self.language_list, 1)

        self.empty_search_label = Label(_("No language found"), "muted", content)
        self.empty_search_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_search_label.hide()
        content_layout.addWidget(self.empty_search_label)

        self.no_dictionaries = QWidget(content)
        no_dict_layout = QVBoxLayout(self.no_dictionaries)
        no_dict_layout.setContentsMargins(0, 30, 0, 30)
        no_dict_layout.addWidget(
            Label(_("No dictionary available"), "row_title", self.no_dictionaries),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        no_dict_description = Label(
            _("Install or configure a dictionary to use the spell checker."),
            "row_description",
            self.no_dictionaries,
        )
        no_dict_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_dict_layout.addWidget(no_dict_description)
        self.no_dictionaries.hide()
        content_layout.addWidget(self.no_dictionaries, 1)
        root.addWidget(content, 1)

        footer = QFrame(self)
        footer.setObjectName("SpellcheckPickerFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(22, 14, 22, 14)
        footer_layout.setSpacing(8)
        self.manage_button = Button(_("Manage dictionaries"), parent=footer)
        self.cancel_button = Button(_("Cancel"), parent=footer)
        self.apply_button = Button(_("Apply"), Button.PRIMARY, footer)
        self.apply_button.setDefault(True)
        self.manage_button.setAccessibleDescription(
            _("Open the spell checker dictionary settings."))
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        footer_layout.addWidget(self.manage_button)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.apply_button)
        root.addWidget(footer)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog#SpellcheckLanguagePickerDialog {
                background: palette(window);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
            QFrame#SpellcheckPickerHeader, QFrame#SpellcheckPickerFooter {
                background: palette(button);
                border: 0;
            }
            QListWidget#SpellcheckLanguageList {
                border: 1px solid palette(mid);
                border-radius: 8px;
                background: palette(base);
                color: palette(text);
                padding: 4px;
                outline: 0;
            }
            QListWidget#SpellcheckLanguageList::item {
                min-height: 30px;
                padding: 3px 8px;
                border-radius: 6px;
            }
            QListWidget#SpellcheckLanguageList::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QListWidget#SpellcheckLanguageList::item:disabled {
                color: palette(placeholder-text);
            }
            QLabel#SpellcheckPickerFeedback {
                color: palette(highlight);
            }
        """)

    @staticmethod
    def _search_key(value):
        decomposed = unicodedata.normalize("NFKD", value or "")
        return "".join(
            char for char in decomposed if not unicodedata.combining(char)
        ).casefold()

    def _populate_languages(self):
        self._updating_list = True
        current_letter = None
        for option in self.options:
            letter = self._search_key(option.label)[:1].upper() or "#"
            if letter != current_letter:
                header = QListWidgetItem(letter, self.language_list)
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                self._letter_items.append(header)
                current_letter = letter
            item = QListWidgetItem(option.label, self.language_list)
            item.setData(self.CODE_ROLE, option.code)
            locale = QLocale(option.code)
            native_terms = " ".join(
                term
                for term in (
                    locale.nativeLanguageName(),
                    locale.nativeTerritoryName(),
                )
                if term
            )
            item.setData(
                self.SEARCH_ROLE,
                self._search_key(
                    f"{option.label} {option.code} {native_terms}"
                ),
            )
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(
                Qt.CheckState.Checked
                if option.code in self._selected
                else Qt.CheckState.Unchecked
            )
            item.setData(Qt.ItemDataRole.AccessibleTextRole, option.label)
            self._language_items[option.code] = item
        self._updating_list = False
        has_options = bool(self.options)
        self.language_list.setVisible(has_options)
        self.all_languages_label.setVisible(has_options)
        self.search_edit.setEnabled(has_options)
        self.no_dictionaries.setVisible(not has_options)

    def _filter_languages(self, text):
        query = self._search_key(text.strip())
        matches = 0
        for header in self._letter_items:
            header.setHidden(bool(query))
        for item in self._language_items.values():
            visible = not query or query in item.data(self.SEARCH_ROLE)
            item.setHidden(not visible)
            matches += int(visible)
        self.empty_search_label.setVisible(bool(query) and matches == 0)
        self.language_list.setVisible(bool(self.options) and matches > 0)

    def _on_item_changed(self, item):
        if self._updating_list:
            return
        code = item.data(self.CODE_ROLE)
        if not code:
            return
        checked = item.checkState() == Qt.CheckState.Checked
        if checked and code not in self._selected:
            self._add_language(code)
        elif not checked and code in self._selected:
            self._remove_language(code)

    def _add_language(self, code):
        if code in self._selected:
            return
        if len(self._selected) >= self.maximum_selected:
            self._show_feedback(_("You can select up to 10 languages."))
            self._set_item_checked(code, False)
            return
        self._selected.append(code)
        self._refresh_selection()

    def _remove_language(self, code):
        if code not in self._selected:
            return
        if len(self._selected) == 1:
            self._show_feedback(_("At least one language must remain selected."))
            self._set_item_checked(code, True)
            return
        self._selected.remove(code)
        self._refresh_selection()

    def _set_item_checked(self, code, checked):
        item = self._language_items.get(code)
        if item is None:
            return
        self._updating_list = True
        item.setCheckState(
            Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        )
        self._updating_list = False

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _refresh_selection(self):
        self._clear_layout(self.selected_layout)
        for code in self._selected:
            option = self._option_by_code[code]
            chip = Button(f"{option.label} ×", parent=self.selected_container)
            chip.setObjectName("SelectedLanguageChip")
            chip.setAccessibleName(_("Remove {language}").format(language=option.label))
            chip.setAccessibleDescription(
                _("Remove this language from the temporary selection."))
            chip.clicked.connect(lambda _checked=False, value=code: self._remove_language(value))
            self.selected_layout.addWidget(chip)

        count = len(self._selected)
        self.selected_count_label.setText(
            f"{count}/{self.maximum_selected}"
        )
        self.selected_count_label.setAccessibleName(
            _("{count} of {maximum} languages selected").format(
                count=count,
                maximum=self.maximum_selected,
            )
        )
        self._refresh_recent()
        at_limit = count >= self.maximum_selected
        for code, item in self._language_items.items():
            flags = item.flags()
            should_enable = code in self._selected or not at_limit
            if should_enable:
                flags |= Qt.ItemFlag.ItemIsEnabled
                item.setToolTip("")
            else:
                flags &= ~Qt.ItemFlag.ItemIsEnabled
                item.setToolTip(_("You can select up to 10 languages."))
            self._updating_list = True
            item.setFlags(flags)
            item.setCheckState(
                Qt.CheckState.Checked
                if code in self._selected
                else Qt.CheckState.Unchecked
            )
            state = _("selected") if code in self._selected else _("not selected")
            item.setData(
                Qt.ItemDataRole.AccessibleTextRole,
                f"{self._option_by_code[code].label}, {state}",
            )
            self._updating_list = False
        self.apply_button.setEnabled(
            bool(self._selected)
            and tuple(self._selected) != self._original_selected
        )
        self.feedback_label.hide()
        self.selected_container.updateGeometry()

    def _refresh_recent(self):
        self._clear_layout(self.recent_layout)
        visible_recent = [
            code for code in self._recent if code not in self._selected
        ][:self.maximum_recent]
        for code in visible_recent:
            option = self._option_by_code[code]
            button = Button(option.label, parent=self.recent_container)
            button.setAccessibleName(_("Add {language}").format(language=option.label))
            button.setAccessibleDescription(
                _("Add this recent language to the temporary selection."))
            at_limit = len(self._selected) >= self.maximum_selected
            button.setEnabled(not at_limit)
            if at_limit:
                button.setToolTip(_("You can select up to 10 languages."))
            button.clicked.connect(lambda _checked=False, value=code: self._add_language(value))
            self.recent_layout.addWidget(button)
        self.recent_section.setVisible(bool(visible_recent))

    def _show_feedback(self, message):
        self.feedback_label.setText(message)
        self.feedback_label.setAccessibleDescription(message)
        self.feedback_label.show()
        self.feedback_label.setFocus(Qt.FocusReason.OtherFocusReason)

    def _fit_to_screen(self):
        screen = self.screen()
        available = screen.availableGeometry().size() if screen else QSize(720, 760)
        width = min(680, max(360, int(available.width() * 0.9)))
        height = min(700, max(480, int(available.height() * 0.9)))
        self.setMinimumSize(min(500, width), min(520, height))
        self.resize(width, height)
        self.setMaximumSize(available)

    def _setup_tab_order(self):
        self.setTabOrder(self.search_edit, self.language_list)
        self.setTabOrder(self.language_list, self.manage_button)
        self.setTabOrder(self.manage_button, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.apply_button)

    def showEvent(self, event):
        super().showEvent(event)
        self.search_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if self.search_edit.text():
                self.search_edit.clear()
            else:
                self.reject()
            event.accept()
            return
        super().keyPressEvent(event)
