"""Native picker for one screen or window exposed by Qt models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from gettext import gettext as _

from PyQt6.QtCore import (
    QAbstractItemModel,
    QItemSelectionModel,
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
)
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QListView,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.ui.primitives import Button, CloseButton, Label


class DesktopMediaKind(Enum):
    """The Qt model that owns a selected desktop-media source."""

    SCREEN = "screen"
    WINDOW = "window"


@dataclass(frozen=True)
class DesktopMediaSelection:
    """A stable reference to one index from an original Qt source model."""

    kind: DesktopMediaKind
    index: QPersistentModelIndex


class DesktopMediaPickerDialog(QDialog):
    """Present dynamic Qt screen/window models without choosing a default."""

    WINDOW_RADIUS = 18
    OUTER_MARGIN = 14

    def __init__(
        self,
        screens_model: QAbstractItemModel | None,
        windows_model: QAbstractItemModel | None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._models = {
            DesktopMediaKind.SCREEN: screens_model,
            DesktopMediaKind.WINDOW: windows_model,
        }
        self._selection: DesktopMediaSelection | None = None
        self._accepted_selection: DesktopMediaSelection | None = None
        self._rejection_reason = "dialog_closed"
        self._changing_selection = False
        self._selection_loss_pending = False

        self.setObjectName("DesktopMediaPickerDialog")
        self.setWindowTitle(_("Share screen or window"))
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._setup_ui()
        self._connect_models()
        self._apply_style()
        self._setup_tab_order()
        self._fit_to_screen()
        self._refresh_empty_states()
        self._refresh_confirmation()

    @property
    def selection(self) -> DesktopMediaSelection | None:
        """Return the accepted source, or ``None`` after any rejection."""
        return self._accepted_selection

    @property
    def rejection_reason(self) -> str:
        return self._rejection_reason

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
        self.window_frame.setObjectName("DesktopMediaPickerWindowFrame")
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
        header.setObjectName("DesktopMediaPickerHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(26, 18, 18, 16)
        header_layout.setSpacing(14)

        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(4)
        self.title_label = Label(
            _("Share screen or window"),
            "section_title",
            header,
        )
        self.description_label = Label(
            _("Only the screen or window you choose will be shared."),
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
        self.close_button.setAccessibleDescription(
            _("Cancel desktop media sharing."))
        header_layout.addLayout(heading_layout, 1)
        header_layout.addWidget(
            self.close_button,
            alignment=Qt.AlignmentFlag.AlignTop,
        )
        window_layout.addWidget(header)

        content = QWidget(self.window_frame)
        content.setObjectName("DesktopMediaPickerContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(26, 12, 26, 18)
        content_layout.setSpacing(10)

        self.source_tabs = QTabWidget(content)
        self.source_tabs.setAccessibleName(_("Source category"))
        self.source_tabs.setAccessibleDescription(
            _("Choose whether to share a screen or a window."))

        screen_page, self.screen_list, self.screen_empty_label = (
            self._create_source_page(
                DesktopMediaKind.SCREEN,
                _("Screens"),
                _("No screens are available."),
                content,
            )
        )
        window_page, self.window_list, self.window_empty_label = (
            self._create_source_page(
                DesktopMediaKind.WINDOW,
                _("Windows"),
                _("No windows are available."),
                content,
            )
        )
        self.source_tabs.addTab(screen_page, _("Screens"))
        self.source_tabs.addTab(window_page, _("Windows"))
        content_layout.addWidget(self.source_tabs, 1)
        window_layout.addWidget(content, 1)

        footer = QFrame(self.window_frame)
        footer.setObjectName("DesktopMediaPickerFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(22, 14, 22, 14)
        footer_layout.setSpacing(8)
        self.cancel_button = Button(_("Cancel"), parent=footer)
        self.share_button = Button(
            _("Share"),
            Button.PRIMARY,
            footer,
        )
        self.cancel_button.setAccessibleName(_("Cancel"))
        self.cancel_button.setAccessibleDescription(
            _("Cancel desktop media sharing."))
        self.share_button.setAccessibleName(_("Share selected source"))
        self.share_button.setAccessibleDescription(
            _("Share the explicitly selected screen or window."))
        self.share_button.setDefault(True)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.share_button)
        window_layout.addWidget(footer)

        self.close_button.clicked.connect(self._close_from_button)
        self.cancel_button.clicked.connect(self._cancel_from_button)
        self.share_button.clicked.connect(self._accept_if_valid)

    def _create_source_page(self, kind, accessible_name, empty_text, parent):
        page = QWidget(parent)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(0)

        stack = QStackedWidget(page)
        source_list = QListView(stack)
        source_list.setObjectName(
            "DesktopMediaScreenList"
            if kind == DesktopMediaKind.SCREEN
            else "DesktopMediaWindowList"
        )
        source_list.setModel(self._models[kind])
        source_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        source_list.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        source_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        source_list.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        source_list.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        source_list.setAccessibleName(accessible_name)
        source_list.setAccessibleDescription(
            _("Select one source. Nothing is selected automatically."))

        empty_label = Label(empty_text, "muted", stack)
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setAccessibleName(empty_text)

        stack.addWidget(source_list)
        stack.addWidget(empty_label)
        layout.addWidget(stack)

        selection_model = source_list.selectionModel()
        if selection_model is not None:
            selection_model.clearSelection()
            selection_model.setCurrentIndex(
                QModelIndex(),
                QItemSelectionModel.SelectionFlag.NoUpdate,
            )
            selection_model.selectionChanged.connect(
                self._on_screen_selection_changed
                if kind == DesktopMediaKind.SCREEN
                else self._on_window_selection_changed
            )
        source_list.activated.connect(self._accept_if_valid)
        source_list.doubleClicked.connect(self._accept_if_valid)

        if kind == DesktopMediaKind.SCREEN:
            self._screen_stack = stack
        else:
            self._window_stack = stack
        return page, source_list, empty_label

    def _connect_models(self):
        for kind, model in self._models.items():
            if model is None:
                continue
            model.rowsInserted.connect(self._on_rows_inserted)
            if kind == DesktopMediaKind.SCREEN:
                model.rowsAboutToBeRemoved.connect(
                    self._on_screen_rows_about_to_be_removed
                )
                model.destroyed.connect(self._on_screen_model_destroyed)
            else:
                model.rowsAboutToBeRemoved.connect(
                    self._on_window_rows_about_to_be_removed
                )
                model.destroyed.connect(self._on_window_model_destroyed)
            model.rowsRemoved.connect(self._on_rows_removed)
            model.modelAboutToBeReset.connect(self._on_model_about_to_reset)
            model.modelReset.connect(self._on_model_reset)
            model.layoutChanged.connect(self._on_layout_changed)

    def _on_screen_selection_changed(self, _selected, _deselected):
        self._on_selection_changed(DesktopMediaKind.SCREEN)

    def _on_window_selection_changed(self, _selected, _deselected):
        self._on_selection_changed(DesktopMediaKind.WINDOW)

    def _on_selection_changed(self, kind: DesktopMediaKind):
        if self._changing_selection:
            return
        source_list = self._list_for(kind)
        selected = source_list.selectionModel().selectedIndexes()
        selected = [index for index in selected if index.column() == 0]
        if not selected:
            if self._selection is not None and self._selection.kind == kind:
                if self._selection_loss_pending:
                    self._refresh_confirmation()
                    return
                if not self._selection.index.isValid():
                    self._invalidate_selection()
                    return
                # QAbstractItemView clears its selection during
                # rowsAboutToBeRemoved before our model observer runs. Keep
                # the persistent index until rowsRemoved can determine
                # whether the selected source actually disappeared.
            self._refresh_confirmation()
            return

        index = selected[0]
        if index.model() is not self._models[kind] or not index.isValid():
            self._invalidate_selection()
            return

        other_kind = (
            DesktopMediaKind.WINDOW
            if kind == DesktopMediaKind.SCREEN
            else DesktopMediaKind.SCREEN
        )
        other_selection_model = self._list_for(other_kind).selectionModel()
        self._changing_selection = True
        try:
            if other_selection_model is not None:
                other_selection_model.clearSelection()
                other_selection_model.setCurrentIndex(
                    QModelIndex(),
                    QItemSelectionModel.SelectionFlag.NoUpdate,
                )
        finally:
            self._changing_selection = False

        self._selection = DesktopMediaSelection(
            kind,
            QPersistentModelIndex(index),
        )
        self._refresh_confirmation()

    def _on_rows_inserted(self, _parent, _first, _last):
        self._refresh_empty_states()

    def _on_screen_rows_about_to_be_removed(self, parent, first, last):
        self._on_rows_about_to_be_removed(
            DesktopMediaKind.SCREEN,
            parent,
            first,
            last,
        )

    def _on_window_rows_about_to_be_removed(self, parent, first, last):
        self._on_rows_about_to_be_removed(
            DesktopMediaKind.WINDOW,
            parent,
            first,
            last,
        )

    def _on_rows_about_to_be_removed(self, kind, parent, first, last):
        selection = self._selection
        if selection is None or selection.kind != kind:
            return
        index = selection.index
        if index.parent() == parent and first <= index.row() <= last:
            self._selection_loss_pending = True
            self.share_button.setEnabled(False)

    def _on_rows_removed(self, _parent, _first, _last):
        self._refresh_empty_states()
        if self._selection_loss_pending:
            self._invalidate_selection()
            return
        self._refresh_selection()

    def _on_model_about_to_reset(self):
        if self._selection is not None:
            self._selection_loss_pending = True
            self.share_button.setEnabled(False)

    def _on_model_reset(self):
        self._refresh_empty_states()
        if self._selection_loss_pending:
            self._invalidate_selection()

    def _on_layout_changed(self, *_args):
        self._refresh_selection()

    def _on_screen_model_destroyed(self, _object=None):
        self._on_model_destroyed(DesktopMediaKind.SCREEN)

    def _on_window_model_destroyed(self, _object=None):
        self._on_model_destroyed(DesktopMediaKind.WINDOW)

    def _on_model_destroyed(self, kind):
        had_selection = (
            self._selection is not None and self._selection.kind == kind
        )
        self._models[kind] = None
        self._refresh_empty_states()
        if had_selection or all(model is None for model in self._models.values()):
            self._invalidate_selection()

    def _refresh_selection(self):
        if self._selection is not None and not self._selection_is_valid():
            self._invalidate_selection()
            return
        self._refresh_confirmation()

    def _invalidate_selection(self):
        self._selection = None
        self._selection_loss_pending = False
        self.share_button.setEnabled(False)
        self._rejection_reason = "invalid_selection"
        self.reject()

    def _selection_is_valid(self) -> bool:
        selection = self._selection
        if selection is None or not selection.index.isValid():
            return False
        model = self._models.get(selection.kind)
        return model is not None and selection.index.model() is model

    def _refresh_confirmation(self):
        self.share_button.setEnabled(self._selection_is_valid())

    def _refresh_empty_states(self):
        for kind, stack in (
            (DesktopMediaKind.SCREEN, self._screen_stack),
            (DesktopMediaKind.WINDOW, self._window_stack),
        ):
            model = self._models[kind]
            try:
                has_sources = model is not None and model.rowCount() > 0
            except RuntimeError:
                has_sources = False
            stack.setCurrentIndex(0 if has_sources else 1)

    def _list_for(self, kind):
        return (
            self.screen_list
            if kind == DesktopMediaKind.SCREEN
            else self.window_list
        )

    def _accept_if_valid(self, _index=None):
        if not self._selection_is_valid():
            self._refresh_confirmation()
            return
        self._accepted_selection = DesktopMediaSelection(
            self._selection.kind,
            QPersistentModelIndex(self._selection.index),
        )
        self.accept()

    def _cancel_from_button(self):
        self._rejection_reason = "user_cancelled"
        self.reject()

    def _close_from_button(self):
        self._rejection_reason = "dialog_closed"
        self.reject()

    def _setup_tab_order(self):
        self.setTabOrder(self.source_tabs, self.screen_list)
        self.setTabOrder(self.screen_list, self.window_list)
        self.setTabOrder(self.window_list, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.share_button)
        self.setTabOrder(self.share_button, self.close_button)

    def _fit_to_screen(self):
        screen = self.screen()
        available = (
            screen.availableGeometry().size()
            if screen is not None
            else QSize(720, 640)
        )
        width = min(680, max(280, int(available.width() * 0.9)))
        height = min(560, max(300, int(available.height() * 0.85)))
        self.setMinimumSize(min(480, width), min(400, height))
        self.resize(width, height)
        self.setMaximumSize(available)

    def _apply_style(self):
        self.setStyleSheet(
            """
            QDialog#DesktopMediaPickerDialog {
                background: transparent;
                color: palette(text);
            }
            QFrame#DesktopMediaPickerWindowFrame {
                background: palette(window);
                border: 1px solid palette(mid);
                border-radius: %dpx;
            }
            QFrame#DesktopMediaPickerHeader,
            QFrame#DesktopMediaPickerFooter,
            QWidget#DesktopMediaPickerContent {
                background: transparent;
                border: 0;
            }
            QListView#DesktopMediaScreenList,
            QListView#DesktopMediaWindowList {
                background: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 9px;
                padding: 4px;
                outline: 0;
            }
            QListView#DesktopMediaScreenList::item,
            QListView#DesktopMediaWindowList::item {
                min-height: 34px;
                padding: 5px 8px;
                border-radius: 6px;
            }
            QListView#DesktopMediaScreenList::item:selected,
            QListView#DesktopMediaWindowList::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QListView#DesktopMediaScreenList:focus,
            QListView#DesktopMediaWindowList:focus,
            QTabWidget:focus {
                border: 2px solid palette(highlight);
            }
            """
            % self.WINDOW_RADIUS
        )

    def showEvent(self, event):
        super().showEvent(event)
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.frameGeometry().center() - self.rect().center())
        self.screen_list.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self._rejection_reason = "user_cancelled"
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)
