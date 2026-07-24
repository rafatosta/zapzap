"""View for the advanced customizations settings page."""

from gettext import gettext as _

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QVBoxLayout, QWidget

from zapzap.ui.components import Button, Label
from zapzap.features.settings.components import (
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsSection,
    SettingsSelectRow,
    SettingsSwitchRow,
)


class CustomizationFilesPanel(QWidget):
    """Compact, shared file-management presentation for CSS and JavaScript."""

    edit_requested = pyqtSignal()
    duplicate_requested = pyqtSignal()
    location_requested = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, empty_title, empty_description, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        header = QtWidgets.QHBoxLayout()
        title = Label(_("Files"), "row_title")
        title.setObjectName("SettingsRowTitle")
        self.create_button = Button(_("+ Create"))
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.create_button)
        layout.addLayout(header)

        self.table = QtWidgets.QTableWidget(self)
        self._setup_table()
        layout.addWidget(self.table)

        self.empty_state = QWidget(self)
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setContentsMargins(12, 8, 12, 8)
        empty_layout.setSpacing(2)
        empty_title_label = Label(empty_title, "row_title")
        empty_description_label = Label(empty_description, "row_description")
        empty_description_label.setWordWrap(True)
        empty_layout.addWidget(empty_title_label)
        empty_layout.addWidget(empty_description_label)
        self.empty_state.setObjectName("CustomizationEmptyState")
        layout.addWidget(self.empty_state)
        self.update_row_count(0)

        actions = QtWidgets.QHBoxLayout()
        self.import_button = Button(_("Import file"))
        self.import_url_button = Button(_("Import URL"))
        self.folder_button = Button(_("Open folder"))
        actions.addWidget(self.import_button)
        actions.addWidget(self.import_url_button)
        actions.addStretch(1)
        actions.addWidget(self.folder_button)
        layout.addLayout(actions)

    def _setup_table(self):
        table = self.table
        table.setObjectName("CustomizationAssetTable")
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        table.setColumnCount(3)
        table.setRowCount(0)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(38)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 44)
        table.setColumnWidth(2, 42)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setStyleSheet("""
            QTableWidget#CustomizationAssetTable {
                background: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 10px;
                outline: 0;
            }
            QTableWidget#CustomizationAssetTable::item {
                border: 0;
                border-bottom: 1px solid palette(midlight);
                padding: 5px 8px;
            }
            QWidget#CustomizationEmptyState {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)

    def update_row_count(self, count):
        self.table.setVisible(count > 0)
        self.empty_state.setVisible(count == 0)
        if count:
            visible_rows = min(count, 6)
            self.table.setFixedHeight(visible_rows * 38 + 2)

    def create_actions_button(self, parent=None, row=None):
        button = QtWidgets.QToolButton(parent)
        button.setText("⋮")
        button.setToolTip(_("File actions"))
        button.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QtWidgets.QMenu(button)
        menu.addAction(_("Edit"), self.edit_requested.emit)
        menu.addAction(_("Duplicate"), self.duplicate_requested.emit)
        menu.addAction(_("Open location"), self.location_requested.emit)
        menu.addSeparator()
        delete_action = menu.addAction(_("Delete"), self.delete_requested.emit)
        delete_action.setProperty("destructive", True)
        if row is not None and isinstance(parent, QtWidgets.QTableWidget):
            menu.aboutToShow.connect(lambda: parent.setCurrentCell(row, 1))
        button.setMenu(menu)
        return button

    def set_dependent_enabled(self, enabled):
        self.table.setEnabled(enabled)
        self.create_button.setEnabled(enabled)
        self.import_button.setEnabled(enabled)
        self.import_url_button.setEnabled(enabled)
        self.folder_button.setEnabled(enabled)
        opacity = QtWidgets.QGraphicsOpacityEffect(self)
        opacity.setOpacity(1.0 if enabled else 0.55)
        self.setGraphicsEffect(opacity)


class AdvancedCustomizationsSettingsView(SettingsPage):
    """Composable advanced customizations view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Advanced customizations"),
            _("Add custom CSS and JavaScript to WhatsApp Web."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_scope_section()
        self._setup_feedback_label()
        self._setup_customizations_section()
        self._setup_pending_bar()

    def _setup_scope_section(self):
        section = SettingsSection(
            _("Scope"),
            _("Choose whether customizations apply to all accounts or only to the current account."),
        )
        card = SettingsCard()
        self.scope_row = SettingsSelectRow(
            _("Apply to"),
            _("Account customizations can inherit or extend the global configuration."),
            [""],
        )
        self.scope_combo = self.scope_row.combo
        self.account_label = Label("", "row_description")
        self.account_label.setObjectName("SettingsRowDescription")
        self.account_label.setWordWrap(True)
        self.inherit_row = SettingsSwitchRow(
            _("Inherit global settings"),
            _("Use only the global customizations for this account."),
        )
        self.inherit_checkbox = self.inherit_row.checkbox
        self.account_scope_hint_label = self.inherit_row
        card.add_row(self.scope_row)
        card.add_row(self.account_label)
        card.add_row(self.inherit_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_feedback_label(self):
        self.feedback_label = Label("", "row_description", self)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setObjectName("SettingsRowDescription")
        self.content_layout.addWidget(self.feedback_label)

    def _setup_customizations_section(self):
        section = SettingsSection(
            _("Customizations"),
            _("Manage custom files for the selected scope."),
        )
        self.customization_tabs = QtWidgets.QTabWidget(self)
        self.customization_tabs.setObjectName("CustomizationTabs")
        self.customization_tabs.setDocumentMode(True)
        self.customization_tabs.tabBar().setDrawBase(False)
        self.customization_tabs.tabBar().setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.customization_tabs.addTab(self._build_css_tab(), _("CSS"))
        self.customization_tabs.addTab(self._build_js_tab(), _("JavaScript"))
        self.customization_tabs.setStyleSheet("""
            QTabWidget#CustomizationTabs::pane {
                border: 0;
                background: transparent;
                margin-top: 6px;
            }
            QTabWidget#CustomizationTabs QTabBar {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
            QTabWidget#CustomizationTabs QTabBar::tab {
                min-width: 104px;
                min-height: 26px;
                padding: 5px 14px;
                margin: 2px;
                border: 0;
                border-radius: 7px;
                background: transparent;
                color: palette(placeholder-text);
            }
            QTabWidget#CustomizationTabs QTabBar::tab:hover:!selected {
                background: palette(window);
                color: palette(text);
            }
            QTabWidget#CustomizationTabs QTabBar::tab:selected {
                background: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
            }
            QTabWidget#CustomizationTabs QTabBar::tab:disabled {
                color: palette(mid);
            }
        """)
        section.layout.addWidget(self.customization_tabs)
        self.add_section(section)

    def _build_css_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(8)
        card = SettingsCard()
        self.css_files_group = card
        self.css_enabled_row = SettingsSwitchRow(
            _("Custom CSS"),
            _("Enables or disables all CSS files in this scope."),
        )
        self.css_enabled = self.css_enabled_row.checkbox
        card.add_row(self.css_enabled_row)
        self.css_panel = CustomizationFilesPanel(
            _("No CSS files"),
            _("Create or import a style to get started."),
            card,
        )
        self.css_files = self.css_panel.table
        card.add_row(self.css_panel)
        layout.addWidget(card)
        layout.addWidget(self._build_preview())
        return tab

    def _build_preview(self):
        card = SettingsCard()
        title = Label(_("Preview"), "row_title")
        title.setObjectName("SettingsRowTitle")
        card.add_row(title)
        self.css_preview_stack = QtWidgets.QStackedWidget(card)
        self.css_preview_stack.setObjectName("CustomizationPreview")
        self.css_preview_stack.setMinimumHeight(88)
        self.css_preview_stack.setMaximumHeight(360)

        self.css_preview_placeholder_page = QWidget()
        placeholder_layout = QVBoxLayout(self.css_preview_placeholder_page)
        self.css_preview_placeholder = Label(
            _("No preview available. Select a CSS file to view an associated screenshot."),
            "row_description",
        )
        self.css_preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.css_preview_placeholder.setWordWrap(True)
        self.css_preview_placeholder_upload_button = Button(_("Upload preview image"))
        self.css_preview_placeholder_upload_button.setVisible(False)
        placeholder_layout.addWidget(self.css_preview_placeholder)
        placeholder_layout.addWidget(
            self.css_preview_placeholder_upload_button,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        self.css_preview_image_page = QWidget()
        image_layout = QtWidgets.QGridLayout(self.css_preview_image_page)
        self.css_preview_image = Label("", "body")
        self.css_preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.css_preview_replace_button = Button(_("Replace preview image"))
        self.css_preview_replace_button.setVisible(False)
        image_layout.addWidget(self.css_preview_image, 0, 0)
        image_layout.addWidget(
            self.css_preview_replace_button, 0, 0, Qt.AlignmentFlag.AlignCenter
        )
        self.css_preview_stack.addWidget(self.css_preview_placeholder_page)
        self.css_preview_stack.addWidget(self.css_preview_image_page)
        card.add_row(self.css_preview_stack)
        return card

    def _build_js_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 10, 0, 0)
        card = SettingsCard()
        self.js_files_group = card
        self.js_enabled_row = SettingsSwitchRow(
            _("Custom JavaScript"),
            _("Enables or disables all JavaScript files in this scope."),
        )
        self.js_enabled = self.js_enabled_row.checkbox
        card.add_row(self.js_enabled_row)
        self.warning_label = SettingsInfoBox(
            _("⚠ Custom scripts have full access to page content. Use code only from trusted sources."),
            "warning",
        )
        card.add_row(self.warning_label)
        self.js_panel = CustomizationFilesPanel(
            _("No JavaScript files"),
            _("Create or import a script to get started."),
            card,
        )
        self.js_files = self.js_panel.table
        card.add_row(self.js_panel)
        layout.addWidget(card)
        layout.addStretch(1)
        return tab

    def _setup_pending_bar(self):
        self.pending_bar = QtWidgets.QFrame(self.viewport())
        self.pending_bar.setObjectName("PendingChangesBar")
        layout = QtWidgets.QHBoxLayout(self.pending_bar)
        layout.setContentsMargins(14, 8, 14, 8)
        self.pending_label = Label(_("● There are unsaved changes."), "row_description")
        self.btn_discard = Button(_("Discard"))
        self.btn_save = Button(_("Save"))
        self.btn_save_reload = Button(_("Save and reload"))
        self.btn_reload = Button(_("Reload page"))
        self.btn_reload.setVisible(False)
        self.btn_save.setDefault(True)
        layout.addWidget(self.pending_label)
        layout.addStretch(1)
        layout.addWidget(self.btn_discard)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_save_reload)
        self.pending_bar.setStyleSheet("""
            QFrame#PendingChangesBar {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
        """)
        self.pending_bar.setVisible(False)
        self.pending_bar.raise_()

    def set_pending_changes(self, pending):
        self.pending_bar.setVisible(pending)
        if pending:
            self._position_pending_bar()

    def _position_pending_bar(self):
        margin = 16
        width = max(320, self.viewport().width() - (margin * 2))
        height = self.pending_bar.sizeHint().height()
        self.pending_bar.setGeometry(
            margin,
            self.viewport().height() - height - margin,
            width,
            height,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_pending_bar()

    def set_category_enabled(self, asset_type, enabled):
        panel = self.css_panel if asset_type == "css" else self.js_panel
        panel.set_dependent_enabled(enabled)

    # Compatibility aliases used by the controller.
    @property
    def btn_css_create(self):
        return self.css_panel.create_button

    @property
    def btn_css_import(self):
        return self.css_panel.import_button

    @property
    def btn_css_import_url(self):
        return self.css_panel.import_url_button

    @property
    def btn_css_folder(self):
        return self.css_panel.folder_button

    @property
    def btn_js_create(self):
        return self.js_panel.create_button

    @property
    def btn_js_import(self):
        return self.js_panel.import_button

    @property
    def btn_js_import_url(self):
        return self.js_panel.import_url_button

    @property
    def btn_js_folder(self):
        return self.js_panel.folder_button
