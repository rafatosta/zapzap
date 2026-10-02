"""User interface for the appearance settings page."""

from gettext import gettext as _

from zapzap.ui.primitives import RadioButton
from zapzap.ui.components import SettingsActionRow
from zapzap.ui.components import FloatingMonitoringPanel
from zapzap.ui.components import SettingsRadioGroup
from zapzap.ui.components import SettingsCard
from zapzap.ui.components import SettingsPage
from zapzap.ui.components import SettingsSection
from zapzap.ui.components import SettingsSelectRow
from zapzap.ui.components import SettingsSubgroupHeader
from zapzap.ui.components import SettingsSwitchGroup
from zapzap.ui.components import SettingsSwitchRow


class AppearanceSettingsView(SettingsPage):
    """Composable appearance settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Appearance"),
            _(
                "Adjust interface chrome, quick access, theme, tray icon, "
                "grid view, and window decorations."
            ),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_interface_section()
        self._setup_quick_access_section()
        self._setup_theme_section()
        self._setup_tray_section()
        self._setup_grid_section()
        self._setup_csr_section()

    def _setup_interface_section(self):
        section = SettingsSection(
            _("Interface"),
            _("Show or hide primary application chrome."),
        )
        card = SettingsCard()
        self.interface_card = card
        self.browser_sidebar_row = SettingsSwitchRow(
            _("Browser sidebar"),
            _("Show account navigation in the browser shell."),
        )
        self.mainwindow_menu_row = SettingsSwitchRow(
            _("Menu bar"),
            _("Show the main window menu bar."),
        )
        self.resizable_chat_list_row = SettingsSwitchRow(
            _("Resizable chat list"),
            _(
                "Drag the edge of the WhatsApp Web chat list to change its "
                "width. Double-click the edge to restore the default width."
            ),
        )
        self._configure_row_accessibility(self.resizable_chat_list_row)
        self.scale_row = SettingsSelectRow(
            _("Interface scale"),
            _("Scale the interface for high-DPI or accessibility needs."),
            [f"{scale} %" for scale in range(50, 201, 5)],
        )
        self.browser_sidebar = self.browser_sidebar_row.checkbox
        self.mainwindow_menu = self.mainwindow_menu_row.checkbox
        self.resizable_chat_list = self.resizable_chat_list_row.checkbox
        self.scaleComboBox = self.scale_row.combo
        card.add_row(self.browser_sidebar_row)
        card.add_row(self.mainwindow_menu_row)
        card.add_row(self.resizable_chat_list_row)
        card.add_row(self.scale_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_quick_access_section(self):
        section = SettingsSection(
            _("Quick Access"),
            _(
                "Control the floating monitoring panel and the account "
                "selector integrated into WhatsApp Web. Both are "
                "independent and can be shown at the same time."
            ),
        )
        card = SettingsCard()
        self.floating_monitoring_panel_row = SettingsSwitchRow(
            _("Floating monitoring panel"),
            _("Monitor accounts in a separate window. Closing it only hides it temporarily."),
        )
        self.integrated_account_selector_row = SettingsSwitchRow(
            _("Integrated account selector"),
            _(
                "Show a compact account selector integrated into "
                "WhatsApp Web."
            ),
        )
        self.floating_monitoring_panel_enabled = (
            self.floating_monitoring_panel_row.checkbox
        )
        self.integrated_account_selector_enabled = (
            self.integrated_account_selector_row.checkbox
        )
        for row in (
            self.floating_monitoring_panel_row,
            self.integrated_account_selector_row,
        ):
            self._configure_row_accessibility(row)
        self.floating_mode_row = SettingsSelectRow(
            _("Show panel"),
            _("Choose when the panel appears automatically."),
        )
        self.floating_mode = self.floating_mode_row.combo
        for label, value in (
            (_("Always"), "always"),
            (_("When the main window is hidden"), "when_hidden"),
            (_("On demand"), "on_demand"),
        ):
            self.floating_mode.addItem(label, value)
        self.floating_on_top_row = SettingsSwitchRow(
            _("Keep above other windows"),
            _("Keep the panel visible while working in other applications."),
        )
        positioning = FloatingMonitoringPanel.supports_positioning()
        position_description = (
            _("Restore the panel position the next time ZapZap starts.")
            if positioning else _("Your Wayland desktop controls window placement.")
        )
        self.floating_remember_row = SettingsSwitchRow(
            _("Remember position"), position_description,
        )
        self.floating_lock_row = SettingsSwitchRow(
            _("Lock position"),
            _("Prevent dragging. Unlock directly in the panel to move it again.")
            if positioning else _("Your Wayland desktop controls window placement."),
        )
        self.floating_show_row = SettingsActionRow(
            _("Show monitoring panel"),
            _("Reopen the panel without changing its display mode."),
            _("Show"),
        )
        self.floating_reset_row = SettingsActionRow(
            _("Reset panel position"),
            _("Bring the panel back into the available screen area."),
            _("Reset"),
        )
        self.floating_options_group = card.add_group(
            self.floating_monitoring_panel_row,
            (self.floating_mode_row, self.floating_on_top_row,
             self.floating_remember_row, self.floating_lock_row,
             self.floating_show_row, self.floating_reset_row),
        )
        for row in (
            self.floating_mode_row, self.floating_on_top_row,
            self.floating_remember_row, self.floating_lock_row,
            self.floating_show_row, self.floating_reset_row,
        ):
            self._configure_row_accessibility(row)
        for row in (self.floating_remember_row, self.floating_lock_row, self.floating_reset_row):
            row.setEnabled(positioning)
        card.add_row(self.integrated_account_selector_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_theme_section(self):
        section = SettingsSection(_("Theme"), _("Choose the visual theme."))
        card = SettingsCard()
        self.theme_auto_radioButton = RadioButton(_("Automatic"))
        self.theme_light_radioButton = RadioButton(_("Light"))
        self.theme_dark_radioButton = RadioButton(_("Dark"))
        card.add_row(
            SettingsRadioGroup(
                self.theme_auto_radioButton,
                self.theme_light_radioButton,
                self.theme_dark_radioButton,
            )
        )
        section.add_card(card)
        self.add_section(section)

    def _setup_tray_section(self):
        section = SettingsSection(
            _("Tray icon"),
            _("Control tray icon visibility, style, and unread counter."),
        )
        card = SettingsCard()
        self.tray_groupBox = SettingsSwitchRow(
            _("Show tray icon"),
            _("Display ZapZap in the system notification area."),
        )
        self.notificationCounter_row = SettingsSwitchRow(
            _("Unread counter"),
            _("Show the number of unread messages."),
        )
        self.notificationCounter = self.notificationCounter_row.checkbox
        self.tray_style_header = SettingsSubgroupHeader(_("Icon style"))
        self.tray_default_radioButton = RadioButton(_("Default"))
        self.tray_slight_radioButton = RadioButton(_("Symbolic light"))
        self.tray_sdark_radioButton = RadioButton(_("Symbolic dark"))
        self.tray_style_group = SettingsRadioGroup(
            self.tray_default_radioButton,
            self.tray_slight_radioButton,
            self.tray_sdark_radioButton,
        )
        self._configure_row_accessibility(self.tray_groupBox)
        self._configure_row_accessibility(self.notificationCounter_row)
        self.tray_options_group = card.add_group(
            self.tray_groupBox,
            (
                self.notificationCounter_row,
                self.tray_style_header,
                self.tray_style_group,
            ),
        )
        section.add_card(card)
        self.add_section(section)

    def _setup_grid_section(self):
        section = SettingsSection(
            _("Grid view"),
            _("Choose how many columns are used by grid view."),
        )
        card = SettingsCard()
        self.grid_row = SettingsSelectRow(
            _("Grid columns"),
            _("Number of account columns in grid view."),
            ["2", "3", "4"],
        )
        self.gridColsComboBox = self.grid_row.combo
        card.add_row(self.grid_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_csr_section(self):
        section = SettingsSection(
            _("Window decoration"),
            _("Customize the window controls drawn by ZapZap."),
        )
        card = SettingsCard()
        self.csr_groupBox = SettingsSwitchRow(
            _("Use custom decoration"),
            _("Use window controls drawn by ZapZap."),
        )
        self.csr_theme_row = SettingsSelectRow(
            _("Button style"),
            _("Visual style used by custom window buttons."),
            [""],
        )
        self.csr_theme_comboBox = self.csr_theme_row.combo
        self.csr_show_minimize_row = SettingsSwitchRow(_("Minimize"))
        self.csr_show_maximize_row = SettingsSwitchRow(_("Maximize"))
        self.csr_show_minimize_checkBox = self.csr_show_minimize_row.checkbox
        self.csr_show_maximize_checkBox = self.csr_show_maximize_row.checkbox
        self.csr_visible_buttons_group = SettingsSwitchGroup(
            _("Visible buttons"),
            self.csr_show_minimize_row,
            self.csr_show_maximize_row,
        )
        self.csr_direction_row = SettingsSelectRow(
            _("Button position"),
            _("Place window buttons on the right or left."),
            [""],
        )
        self.csr_direction_comboBox = self.csr_direction_row.combo
        self.csr_direction_comboBox.clear()
        self.csr_direction_comboBox.addItem(_("Right"), "right")
        self.csr_direction_comboBox.addItem(_("Left"), "left")
        for row in (
            self.csr_groupBox,
            self.csr_theme_row,
            self.csr_show_minimize_row,
            self.csr_show_maximize_row,
            self.csr_direction_row,
        ):
            self._configure_row_accessibility(row)
        self.csr_options_group = card.add_group(
            self.csr_groupBox,
            (
                self.csr_theme_row,
                self.csr_visible_buttons_group,
                self.csr_direction_row,
            ),
        )
        section.add_card(card)
        self.add_section(section)

    @staticmethod
    def _configure_row_accessibility(row):
        """Expose visible row copy to keyboard and assistive technology."""
        control = row.control
        if control is None:
            return
        control.setAccessibleName(row.title_label.text())
        description = (
            row.description_label.text()
            if row.description_label is not None
            else row.title_label.text()
        )
        control.setAccessibleDescription(description)
