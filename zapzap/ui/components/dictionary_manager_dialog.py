"""Reusable presentation for managing Qt WebEngine dictionary files."""

from __future__ import annotations

from gettext import gettext as _
import unicodedata

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QProgressBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from zapzap.ui.primitives import Button, CloseButton, ComboBox, Label, LineEdit


class DictionaryManagerDialog(QDialog):
    """Palette-aware dictionary catalog with bounded tree-based presentation."""

    refresh_requested = pyqtSignal(bool)
    install_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    import_files_requested = pyqtSignal(object)
    import_directory_requested = pyqtSignal(str)
    active_languages_requested = pyqtSignal()

    CODE_ROLE = int(Qt.ItemDataRole.UserRole)
    SEARCH_ROLE = CODE_ROLE + 1
    OUTER_MARGIN = 14
    WINDOW_RADIUS = 18

    def __init__(self, parent=None):
        super().__init__(parent)
        self._states = {}
        self._catalog_entries = {}
        self._busy_codes = set()
        self._catalog_available = False
        self._catalog_loading = True
        self.setObjectName("DictionaryManagerDialog")
        self.setWindowTitle(_("Manage dictionaries"))
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(780, 680)
        self._setup_ui()
        self._apply_style()
        self._setup_tab_order()

    @staticmethod
    def _search_key(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value or "")
        return "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        ).casefold()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(*(self.OUTER_MARGIN,) * 4)
        self.window_frame = QFrame(self)
        self.window_frame.setObjectName("DictionaryManagerWindowFrame")
        root.addWidget(self.window_frame)

        shadow = QGraphicsDropShadowEffect(self.window_frame)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.window_frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.window_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame(self.window_frame)
        header.setObjectName("DictionaryManagerHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 16, 18, 16)
        header_layout.addWidget(Label(_("Manage dictionaries"), "section_title", header))
        header_layout.addStretch(1)
        self.close_button = CloseButton(header, tooltip=_("Close"), circular=True)
        self.close_button.clicked.connect(self.reject)
        header_layout.addWidget(self.close_button)
        layout.addWidget(header)

        content = QWidget(self.window_frame)
        content.setObjectName("DictionaryManagerContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(26, 18, 26, 18)
        content_layout.setSpacing(10)
        content_layout.addWidget(
            Label(
                _(
                    "Install dictionaries from the official ZapZap catalog for "
                    "Qt WebEngine spell checking."
                ),
                "row_description",
                content,
            )
        )

        controls = QHBoxLayout()
        self.search_edit = LineEdit(parent=content)
        self.search_edit.setPlaceholderText(_("Search language or code"))
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setAccessibleName(_("Search dictionaries"))
        self.search_edit.setAccessibleDescription(
            _("Filter dictionaries by readable language name or technical code.")
        )
        self.filter_combo = ComboBox(content)
        self.filter_combo.addItem(_("All"), "all")
        self.filter_combo.addItem(_("Installed"), "installed")
        self.filter_combo.addItem(_("Available"), "available")
        self.filter_combo.setAccessibleName(_("Dictionary filter"))
        self.refresh_button = Button(_("Refresh list"), parent=content)
        self.refresh_button.setAccessibleDescription(
            _("Download the latest dictionary catalog."))
        controls.addWidget(self.search_edit, 1)
        controls.addWidget(self.filter_combo)
        controls.addWidget(self.refresh_button)
        content_layout.addLayout(controls)

        self.catalog_status = Label(_("Loading dictionary catalog…"), "muted", content)
        self.catalog_status.setAccessibleName(_("Dictionary catalog status"))
        content_layout.addWidget(self.catalog_status)
        self.active_summary = Label(_("No active dictionary"), "row_description", content)
        self.active_summary.setAccessibleName(_("Active spell checker languages"))
        content_layout.addWidget(self.active_summary)

        self.dictionary_tree = QTreeWidget(content)
        self.dictionary_tree.setObjectName("DictionaryManagerTree")
        self.dictionary_tree.setColumnCount(3)
        self.dictionary_tree.setHeaderLabels([_("Language"), _("Code"), _("Status")])
        self.dictionary_tree.setRootIsDecorated(False)
        self.dictionary_tree.setAlternatingRowColors(True)
        self.dictionary_tree.setSelectionMode(
            QTreeWidget.SelectionMode.ExtendedSelection
        )
        self.dictionary_tree.setAccessibleName(_("Dictionaries"))
        self.dictionary_tree.setAccessibleDescription(
            _("Select a dictionary to install, remove, or inspect its status.")
        )
        self.dictionary_tree.header().setStretchLastSection(False)
        self.dictionary_tree.header().setSectionResizeMode(
            0, self.dictionary_tree.header().ResizeMode.Stretch
        )
        self.dictionary_tree.header().setSectionResizeMode(
            1, self.dictionary_tree.header().ResizeMode.ResizeToContents
        )
        self.dictionary_tree.header().setSectionResizeMode(
            2, self.dictionary_tree.header().ResizeMode.ResizeToContents
        )
        content_layout.addWidget(self.dictionary_tree, 1)

        self.empty_label = Label(_("No dictionary matches this view."), "muted", content)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.hide()
        content_layout.addWidget(self.empty_label)

        self.item_feedback = Label("", "row_description", content)
        self.item_feedback.setObjectName("DictionaryManagerFeedback")
        self.item_feedback.setAccessibleName(_("Dictionary operation status"))
        self.item_feedback.hide()
        content_layout.addWidget(self.item_feedback)

        self.progress_bar = QProgressBar(content)
        self.progress_bar.setAccessibleName(_("Dictionary download progress"))
        self.progress_bar.hide()
        content_layout.addWidget(self.progress_bar)
        layout.addWidget(content, 1)

        footer = QFrame(self.window_frame)
        footer.setObjectName("DictionaryManagerFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(22, 14, 22, 14)
        footer_layout.setSpacing(8)
        self.import_files_button = Button(_("Import files…"), parent=footer)
        self.import_directory_button = Button(_("Import folder…"), parent=footer)
        self.active_button = Button(_("Active languages…"), parent=footer)
        self.install_button = Button(_("Install"), Button.PRIMARY, footer)
        self.remove_button = Button(_("Remove"), Button.DANGER, footer)
        self.cancel_download_button = Button(_("Cancel download"), parent=footer)
        self.close_footer_button = Button(_("Close"), parent=footer)
        footer_layout.addWidget(self.import_files_button)
        footer_layout.addWidget(self.import_directory_button)
        footer_layout.addWidget(self.active_button)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.install_button)
        footer_layout.addWidget(self.remove_button)
        footer_layout.addWidget(self.cancel_download_button)
        footer_layout.addWidget(self.close_footer_button)
        layout.addWidget(footer)

        self.search_edit.textChanged.connect(self._apply_filter)
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        self.refresh_button.clicked.connect(lambda: self.refresh_requested.emit(True))
        self.dictionary_tree.currentItemChanged.connect(self._selection_changed)
        self.install_button.clicked.connect(self._request_install)
        self.remove_button.clicked.connect(self._request_remove)
        self.cancel_download_button.clicked.connect(self._request_cancel)
        self.active_button.clicked.connect(self.active_languages_requested)
        self.import_files_button.clicked.connect(self._choose_files)
        self.import_directory_button.clicked.connect(self._choose_directory)
        self.close_footer_button.clicked.connect(self.accept)
        self._selection_changed(None, None)

    def _apply_style(self):
        self.setStyleSheet(
            """
            QDialog#DictionaryManagerDialog { background: transparent; }
            QFrame#DictionaryManagerWindowFrame {
                background: palette(window);
                border: 1px solid palette(mid);
                border-radius: %dpx;
            }
            QFrame#DictionaryManagerHeader,
            QFrame#DictionaryManagerFooter,
            QWidget#DictionaryManagerContent {
                background: transparent;
                border: 0;
            }
            QTreeWidget#DictionaryManagerTree {
                border: 1px solid palette(mid);
                border-radius: 8px;
                background: palette(base);
                color: palette(text);
                alternate-background-color: palette(alternate-base);
                outline: 0;
            }
            QTreeWidget#DictionaryManagerTree::item { min-height: 30px; }
            QTreeWidget#DictionaryManagerTree::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QLabel#DictionaryManagerFeedback { color: palette(highlight); }
            """
            % self.WINDOW_RADIUS
        )

    def _setup_tab_order(self):
        widgets = (
            self.search_edit,
            self.filter_combo,
            self.refresh_button,
            self.dictionary_tree,
            self.import_files_button,
            self.import_directory_button,
            self.active_button,
            self.install_button,
            self.remove_button,
            self.cancel_download_button,
            self.close_footer_button,
        )
        for current, following in zip(widgets, widgets[1:]):
            self.setTabOrder(current, following)

    def set_catalog(self, snapshot, states) -> None:
        self._catalog_available = True
        self._catalog_loading = False
        self._catalog_entries = {entry.code: entry for entry in snapshot.entries}
        self._states = {state.code: state for state in states}
        if snapshot.stale:
            self.catalog_status.setText(
                _("Offline catalog from {date}").format(date=snapshot.fetched_at)
            )
        else:
            self.catalog_status.setText(
                _("Catalog {revision}: {count} dictionaries").format(
                    revision=snapshot.revision,
                    count=len(snapshot.entries),
                )
            )
        self._populate()

    def set_installed_only(self, states, *, loading: bool = False) -> None:
        self._catalog_available = False
        self._catalog_loading = loading
        self._states = {state.code: state for state in states}
        if loading:
            self.catalog_status.setText(_("Loading dictionary catalog…"))
        else:
            self.catalog_status.setText(
                _(
                    "The online catalog is unavailable. Installed dictionaries "
                    "remain usable."
                )
            )
        self._populate()

    def set_catalog_error(self, detail: str, using_cache: bool) -> None:
        if using_cache:
            self.item_feedback.setText(
                _("Could not refresh the catalog; using the saved copy. {detail}").format(
                    detail=detail
                )
            )
        else:
            self.item_feedback.setText(
                _("Could not load the dictionary catalog. {detail}").format(
                    detail=detail
                )
            )
        self.item_feedback.show()

    def _populate(self):
        current_code = self.current_code()
        self.dictionary_tree.clear()
        active_labels = [
            state.label for state in self._states.values() if state.active
        ]
        if active_labels:
            self.active_summary.setText(
                _("Active: {languages}").format(languages=", ".join(active_labels))
            )
        else:
            self.active_summary.setText(_("No active dictionary"))
        for state in self._states.values():
            statuses = []
            if state.active:
                statuses.append(_("Active"))
            if state.installed:
                statuses.append(_("Installed"))
            elif state.available:
                statuses.append(_("Available"))
            if state.local:
                statuses.append(_("Local"))
            item = QTreeWidgetItem(
                [state.label, state.code, " · ".join(statuses)]
            )
            item.setData(0, self.CODE_ROLE, state.code)
            item.setData(
                0,
                self.SEARCH_ROLE,
                self._search_key(f"{state.label} {state.code}"),
            )
            item.setData(
                0,
                Qt.ItemDataRole.AccessibleTextRole,
                _("{language}, {code}, {status}").format(
                    language=state.label,
                    code=state.code,
                    status=" · ".join(statuses),
                ),
            )
            self.dictionary_tree.addTopLevelItem(item)
            if state.code == current_code:
                self.dictionary_tree.setCurrentItem(item)
        self._apply_filter()
        self._selection_changed(self.dictionary_tree.currentItem(), None)

    def _apply_filter(self, *_args):
        query = self._search_key(self.search_edit.text().strip())
        mode = self.filter_combo.currentData() or "all"
        visible = 0
        for index in range(self.dictionary_tree.topLevelItemCount()):
            item = self.dictionary_tree.topLevelItem(index)
            code = item.data(0, self.CODE_ROLE)
            state = self._states.get(code)
            matches_mode = (
                mode == "all"
                or (mode == "installed" and state and state.installed)
                or (mode == "available" and state and state.available and not state.installed)
            )
            matches_search = not query or query in item.data(0, self.SEARCH_ROLE)
            item.setHidden(not (matches_mode and matches_search))
            visible += int(not item.isHidden())
        if visible == 0:
            if query:
                empty_text = _("No dictionary matches the search.")
            elif self._catalog_loading:
                empty_text = _("The dictionary catalog is loading.")
            elif mode == "installed":
                empty_text = _("No dictionaries are installed.")
            elif mode == "available" and not self._catalog_available:
                empty_text = _("The available catalog could not be loaded.")
            elif mode == "available":
                empty_text = _("No dictionaries are available to install.")
            else:
                empty_text = _("No dictionaries are installed or available.")
            self.empty_label.setText(empty_text)
        self.empty_label.setVisible(visible == 0)
        self.dictionary_tree.setVisible(visible > 0)

    def current_code(self) -> str:
        item = self.dictionary_tree.currentItem()
        return str(item.data(0, self.CODE_ROLE)) if item else ""

    def selected_codes(self) -> list[str]:
        return [
            str(item.data(0, self.CODE_ROLE))
            for item in self.dictionary_tree.selectedItems()
        ]

    def catalog_entry(self, code: str):
        return self._catalog_entries.get(code)

    def _selection_changed(self, current, _previous):
        selected = [
            self._states[code]
            for code in self.selected_codes()
            if code in self._states
        ]
        installable = [
            state
            for state in selected
            if state.available
            and not state.installed
            and state.code not in self._busy_codes
        ]
        removable = [
            state
            for state in selected
            if state.installed and state.code not in self._busy_codes
        ]
        cancellable = [
            state for state in selected if state.code in self._busy_codes
        ]
        self.install_button.setVisible(bool(installable))
        self.install_button.setEnabled(bool(installable))
        self.remove_button.setVisible(bool(removable))
        self.remove_button.setEnabled(bool(removable))
        self.cancel_download_button.setVisible(bool(cancellable))
        self.active_button.setEnabled(any(state.installed for state in self._states.values()))

    def _request_install(self):
        for code in self.selected_codes():
            state = self._states.get(code)
            if (
                state
                and state.available
                and not state.installed
                and code not in self._busy_codes
            ):
                self.install_requested.emit(code)

    def _request_remove(self):
        for code in self.selected_codes():
            state = self._states.get(code)
            if state and state.installed:
                self.remove_requested.emit(code)

    def _request_cancel(self):
        for code in self.selected_codes():
            if code in self._busy_codes:
                self.cancel_requested.emit(code)

    def _choose_files(self):
        paths, _selected_filter = QFileDialog.getOpenFileNames(
            self,
            _("Import dictionaries"),
            "",
            _("Qt WebEngine dictionaries (*.bdic)"),
        )
        if paths:
            self.import_files_requested.emit(paths)

    def _choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, _("Import dictionary folder"))
        if path:
            self.import_directory_requested.emit(path)

    def set_download_busy(self, code: str, busy: bool) -> None:
        if busy:
            self._busy_codes.add(code)
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            self.item_feedback.setText(
                _("Downloading {code}…").format(code=code)
            )
            self.item_feedback.show()
        else:
            self._busy_codes.discard(code)
            if not self._busy_codes:
                self.progress_bar.hide()
        self._selection_changed(self.dictionary_tree.currentItem(), None)

    def set_download_progress(self, code: str, received: int, total: int) -> None:
        if code != self.current_code():
            return
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(min(received, total))
        else:
            self.progress_bar.setRange(0, 0)

    def set_operation_result(self, result) -> None:
        if result.success:
            self.item_feedback.setText(
                _("Dictionary {code} is ready.").format(code=result.code)
            )
        else:
            self.item_feedback.setText(
                _("Dictionary operation failed: {detail}").format(
                    detail=self._operation_error_message(result.error)
                )
            )
        self.item_feedback.show()

    @staticmethod
    def _operation_error_message(error) -> str:
        messages = {
            "invalid_file": _("The file or filename is invalid."),
            "conflict": _("A different dictionary with this name already exists."),
            "permission": _("ZapZap could not write to the dictionary directory."),
            "disk_full": _("There is not enough free disk space."),
            "last_active": _("The last active dictionary is protected."),
            "not_installed": _("The dictionary is not installed."),
            "cancelled": _("The download was cancelled."),
            "network": _("Check the connection and try again."),
            "timeout": _("The download timed out. Try again."),
            "rate_limit": _("GitHub temporarily limited catalog requests."),
            "http": _("The dictionary server returned an error."),
            "redirect": _("The server redirected to an untrusted address."),
            "size": _("The downloaded size does not match the catalog."),
            "hash": _("The downloaded file failed integrity verification."),
            "busy": _("This dictionary operation is already in progress."),
        }
        value = getattr(error, "value", str(error))
        return messages.get(value, _("Unknown dictionary error."))
