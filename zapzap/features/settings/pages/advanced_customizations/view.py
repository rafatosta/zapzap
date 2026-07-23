"""View for the Customizações avançadas settings page."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFormLayout, QHeaderView, QTableWidgetItem, QVBoxLayout, QWidget

from zapzap.ui.components import Button
from zapzap.ui.components import CheckBox
from zapzap.ui.components import ComboBox
from zapzap.ui.components import Label
from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsInfoBox
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsSection


class AdvancedCustomizationsSettingsView(SettingsPage):
    """Composable advanced customizations view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Advanced Customizations"),
            _("Manage CSS, JavaScript and customizations by scope."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_scope_section()
        self._setup_feedback_label()
        self._setup_css_section()
        self._setup_preview_section()
        self._setup_js_section()
        self._setup_actions_section()

    def _setup_scope_section(self):
        section = SettingsSection(_("Scope"), _("Choose the customization scope."))
        card = SettingsCard()
        scope_row = QWidget()
        scope_layout = QFormLayout(scope_row)
        self.scope_combo = ComboBox(scope_row)
        self.account_label = Label("", "body", scope_row)
        self.account_label.setWordWrap(True)
        scope_layout.addRow(_("Account"), self.scope_combo)
        scope_layout.addRow("", self.account_label)
        self.inherit_checkbox = CheckBox(
            _("Inherit global settings"),
            scope_row,
        )
        self.account_scope_hint_label = Label(
            _("When inherit is disabled, account customizations are appended after global settings."),
            "row_description",
            scope_row,
        )
        self.account_scope_hint_label.setWordWrap(True)
        card.add_row(scope_row)
        card.add_row(self.inherit_checkbox)
        card.add_row(self.account_scope_hint_label)
        section.add_card(card)
        self.add_section(section)

    def _setup_feedback_label(self):
        self.feedback_label = Label("", "row_description", self)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setObjectName("SettingsRowDescription")
        self.content_layout.addWidget(self.feedback_label)

    def _setup_css_section(self):
        section = SettingsSection(
            _("CSS customizations"),
            _("Import, create, edit, enable, and delete CSS files."),
        )
        self.css_files_group = SettingsCard()
        self.css_enabled = CheckBox(
            _("Enable custom CSS"),
            self.css_files_group,
        )
        self.css_files_group.add_row(self.css_enabled)
        self.css_files = QtWidgets.QTableWidget(self.css_files_group)
        self._setup_asset_table(self.css_files)
        self.css_files_group.add_row(self.css_files)

        css_buttons_1 = self._button_row()
        self.btn_css_create = Button(_("Create"))
        self.btn_css_edit = Button(_("Edit"))
        self.btn_css_delete = Button(_("Delete"))
        for button in (self.btn_css_create, self.btn_css_edit, self.btn_css_delete):
            css_buttons_1.layout().addWidget(button)
        css_buttons_1.layout().addStretch(1)

        css_buttons_2 = self._button_row()
        self.btn_css_import = Button(_("Import .css"))
        self.btn_css_import_url = Button(_("Import from URL"))
        self.btn_css_folder = Button(_("Open folder"))
        for button in (self.btn_css_import, self.btn_css_import_url, self.btn_css_folder):
            css_buttons_2.layout().addWidget(button)
        css_buttons_2.layout().addStretch(1)

        self.css_files_group.add_row(css_buttons_1)
        self.css_files_group.add_row(css_buttons_2)
        section.add_card(self.css_files_group)
        self.add_section(section)

    def _setup_preview_section(self):
        section = SettingsSection(
            _("CSS preview"),
            _("Attach and preview a screenshot for the selected CSS file."),
        )
        card = SettingsCard()
        self.css_preview_stack = QtWidgets.QStackedWidget(card)
        self.css_preview_placeholder_page = QWidget()
        placeholder_layout = QVBoxLayout(self.css_preview_placeholder_page)
        self.css_preview_placeholder = Label(_("Select a CSS file to preview."), "body")
        self.css_preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.css_preview_placeholder.setWordWrap(True)
        self.css_preview_placeholder_upload_button = Button(
            _("Upload preview image"),
        )
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
            self.css_preview_replace_button,
            0,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )
        self.css_preview_stack.addWidget(self.css_preview_placeholder_page)
        self.css_preview_stack.addWidget(self.css_preview_image_page)
        card.add_row(self.css_preview_stack)
        section.add_card(card)
        self.add_section(section)

    def _setup_js_section(self):
        section = SettingsSection(
            _("JavaScript customizations"),
            _("Import, create, edit, enable, and delete JavaScript files."),
        )
        self.js_files_group = SettingsCard()
        self.js_enabled = CheckBox(
            _("Enable custom JavaScript"),
            self.js_files_group,
        )
        self.js_files_group.add_row(self.js_enabled)
        self.warning_label = SettingsInfoBox(
            _("⚠ Custom JavaScript runs with full page privileges. Use trusted code only."),
            "warning",
        )
        self.js_files_group.add_row(self.warning_label)
        self.js_files = QtWidgets.QTableWidget(self.js_files_group)
        self._setup_asset_table(self.js_files)
        self.js_files_group.add_row(self.js_files)

        js_buttons_1 = self._button_row()
        self.btn_js_create = Button(_("Create"))
        self.btn_js_edit = Button(_("Edit"))
        self.btn_js_delete = Button(_("Delete"))
        for button in (self.btn_js_create, self.btn_js_edit, self.btn_js_delete):
            js_buttons_1.layout().addWidget(button)
        js_buttons_1.layout().addStretch(1)

        js_buttons_2 = self._button_row()
        self.btn_js_import = Button(_("Import .js"))
        self.btn_js_import_url = Button(_("Import from URL"))
        self.btn_js_folder = Button(_("Open folder"))
        for button in (self.btn_js_import, self.btn_js_import_url, self.btn_js_folder):
            js_buttons_2.layout().addWidget(button)
        js_buttons_2.layout().addStretch(1)

        self.js_files_group.add_row(js_buttons_1)
        self.js_files_group.add_row(js_buttons_2)
        section.add_card(self.js_files_group)
        self.add_section(section)

    def _setup_actions_section(self):
        section = SettingsSection(
            _("Apply changes"),
            _("Save changes and reload target pages when needed."),
        )
        card = SettingsCard()
        action_row = self._button_row()
        self.btn_save_reload = Button(_("Save and reload"))
        self.btn_reload = Button(_("Reload"))
        self.btn_save = Button(_("Save"))
        self.btn_save.setDefault(True)
        action_row.layout().addStretch(1)
        for button in (self.btn_save_reload, self.btn_reload, self.btn_save):
            action_row.layout().addWidget(button)
        card.add_row(action_row)
        section.add_card(card)
        self.add_section(section)

    def _button_row(self):
        row = QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        return row

    def _setup_asset_table(self, table):
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.setColumnCount(2)
        table.setRowCount(0)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(_("Enabled")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(_("Filename")))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(0, 90)
