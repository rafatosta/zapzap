"""User interface for the appearance settings page."""

from gettext import gettext as _

from zapzap.ui.primitives import RadioButton
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
            _("Adjust interface chrome, theme, tray icon, grid view, and window decorations."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_interface_section()
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
        self.browser_sidebar_row = SettingsSwitchRow(
            _("Browser sidebar"),
            _("Show account navigation in the browser shell."),
        )
        self.mainwindow_menu_row = SettingsSwitchRow(
            _("Menu bar"),
            _("Show the main window menu bar."),
        )
        self.scale_row = SettingsSelectRow(
            _("Interface scale"),
            _("Scale the interface for high-DPI or accessibility needs."),
            [f"{scale} %" for scale in range(50, 201, 5)],
        )
        self.browser_sidebar = self.browser_sidebar_row.checkbox
        self.mainwindow_menu = self.mainwindow_menu_row.checkbox
        self.scaleComboBox = self.scale_row.combo
        card.add_row(self.browser_sidebar_row)
        card.add_row(self.mainwindow_menu_row)
        card.add_row(self.scale_row)
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
