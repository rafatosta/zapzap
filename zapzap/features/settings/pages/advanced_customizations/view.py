"""View for the Customizações avançadas settings page."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6 import QtWidgets

from zapzap.ui.components import Button
from zapzap.ui.components import Label
from zapzap.features.settings.components import SettingsActionRow
from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsInfoBox
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsSelectRow
from zapzap.features.settings.components import SettingsSection
from zapzap.features.settings.components import SettingsSwitchRow


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
        section = SettingsSection(
            _("Scope"),
            _("Choose whether customizations apply globally or only to the current account."),
        )
        card = SettingsCard()
        self.scope_row = SettingsSelectRow(
            _("Customization scope"),
            _("Account customizations can extend or inherit the global configuration."),
            [""],
        )
        self.scope_combo = self.scope_row.combo
        self.account_label = Label("", "row_description")
        self.account_label.setObjectName("SettingsRowDescription")
        self.account_label.setWordWrap(True)
        self.inherit_row = SettingsSwitchRow(
            _("Inherit global settings"),
            _("When inherit is disabled, account customizations are appended after global settings."),
        )
        self.inherit_checkbox = self.inherit_row.checkbox
        # Kept as a compatibility alias for the controller, which controls
        # visibility based on the selected scope.
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

    def _setup_css_section(self):
        section = SettingsSection(
            _("CSS customizations"),
            _("Import, create, edit, enable, and delete CSS files."),
        )
        self.css_files_group = SettingsCard()
        self.css_enabled_row = SettingsSwitchRow(
            _("Enable custom CSS"),
            _("Load enabled style files for the selected scope."),
        )
        self.css_enabled = self.css_enabled_row.checkbox
        self.css_files_group.add_row(self.css_enabled_row)
        self.css_files = QtWidgets.QTableWidget(self.css_files_group)
        self._setup_asset_table(self.css_files)
        self.css_files_group.add_row(self.css_files)

        css_buttons_1 = self._button_row()
        self.btn_css_create = Button(_("Create"))
        self.btn_css_edit = Button(_("Edit"))
        self.btn_css_delete = Button(_("Delete"), variant=Button.DANGER)
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
        self.css_preview_stack.setObjectName("CustomizationPreview")
        self.css_preview_stack.setMinimumHeight(240)
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
        self.js_enabled_row = SettingsSwitchRow(
            _("Enable custom JavaScript"),
            _("Load enabled scripts for the selected scope."),
        )
        self.js_enabled = self.js_enabled_row.checkbox
        self.js_files_group.add_row(self.js_enabled_row)
        self.warning_label = SettingsInfoBox(
            _("⚠ Custom JavaScript runs with full page privileges. Use trusted code only."),
            "warning",
        )
        self.js_files_group.add_row(self.warning_label)
        self.js_files_group.add_space()
        self.js_files = QtWidgets.QTableWidget(self.js_files_group)
        self._setup_asset_table(self.js_files)
        self.js_files_group.add_row(self.js_files)

        js_buttons_1 = self._button_row()
        self.btn_js_create = Button(_("Create"))
        self.btn_js_edit = Button(_("Edit"))
        self.btn_js_delete = Button(_("Delete"), variant=Button.DANGER)
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
        self.save_reload_row = SettingsActionRow(
            _("Save and reload"),
            _("Save the selected scope and reload its target page immediately."),
            _("Save and reload"),
        )
        self.reload_row = SettingsActionRow(
            _("Reload target"),
            _("Reload the target page without changing the saved configuration."),
            _("Reload"),
        )
        self.save_row = SettingsActionRow(
            _("Save changes"),
            _("Store changes without reloading the target page."),
            _("Save"),
        )
        self.btn_save_reload = self.save_reload_row.button
        self.btn_reload = self.reload_row.button
        self.btn_save = self.save_row.button
        self.btn_save.setDefault(True)
        card.add_row(self.save_reload_row)
        card.add_row(self.reload_row)
        card.add_row(self.save_row)
        section.add_card(card)
        self.add_section(section)

    def _button_row(self):
        row = QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        return row

    def _setup_asset_table(self, table):
        table.setObjectName("CustomizationAssetTable")
        table.setMinimumHeight(200)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        table.setColumnCount(2)
        table.setRowCount(0)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(_("Enabled")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(_("Filename")))
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(38)
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(0, 90)
        table.setStyleSheet("""
            QTableWidget#CustomizationAssetTable {
                background: palette(base);
                alternate-background-color: palette(alternate-base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 10px;
                outline: 0;
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            QTableWidget#CustomizationAssetTable::item {
                border: 0;
                padding: 6px 8px;
            }
            QHeaderView::section {
                background: palette(alternate-base);
                color: palette(text);
                border: 0;
                border-bottom: 1px solid palette(mid);
                padding: 8px;
            }
        """)
