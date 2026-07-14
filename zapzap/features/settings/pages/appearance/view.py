"""User interface for the appearance settings page."""

from gettext import gettext as _

from zapzap.ui.components import RadioButton
from zapzap.features.settings.components import SettingsActionRow
from zapzap.features.settings.components import SettingsRadioGroup
from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsSection
from zapzap.features.settings.components import SettingsSelectRow
from zapzap.features.settings.components import SettingsSwitchRow


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
            ["50 %", "75 %", "100 %", "125 %", "150 %", "175 %", "200 %"],
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
            _("Enable tray icon"),
            _("Show ZapZap in the system tray."),
        )
        self.notificationCounter_row = SettingsSwitchRow(
            _("Notification counter"),
            _("Show unread notifications on the tray icon."),
        )
        self.notificationCounter = self.notificationCounter_row.checkbox
        self.tray_default_radioButton = RadioButton(_("Default"))
        self.tray_slight_radioButton = RadioButton(_("Symbolic light"))
        self.tray_sdark_radioButton = RadioButton(_("Symbolic dark"))
        card.add_row(self.tray_groupBox)
        card.add_row(self.notificationCounter_row)
        card.add_row(
            SettingsRadioGroup(
                self.tray_default_radioButton,
                self.tray_slight_radioButton,
                self.tray_sdark_radioButton,
            )
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
            _("Custom window decoration"),
            _("Configure client-side rendering window buttons."),
        )
        card = SettingsCard()
        self.csr_groupBox = SettingsSwitchRow(
            _("Use custom window decoration"),
            _("Draw ZapZap window controls instead of native ones."),
        )
        self.csr_theme_row = SettingsSelectRow(
            _("Button theme"),
            _("Theme used by custom window buttons."),
            [""],
        )
        self.csr_theme_comboBox = self.csr_theme_row.combo
        self.csr_show_minimize_row = SettingsSwitchRow(_("Show minimize button"))
        self.csr_show_maximize_row = SettingsSwitchRow(_("Show maximize button"))
        self.csr_show_minimize_checkBox = self.csr_show_minimize_row.checkbox
        self.csr_show_maximize_checkBox = self.csr_show_maximize_row.checkbox
        self.csr_direction_row = SettingsSelectRow(
            _("Button direction"),
            _("Place window buttons on the right or left."),
            ["right", "left"],
        )
        self.csr_direction_comboBox = self.csr_direction_row.combo
        self.restart_interface_row = SettingsActionRow(
            _("Restart interface"),
            _("Rebuild the main window to apply window decoration mode changes."),
            _("Restart interface"),
        )
        self.btn_restart_interface = self.restart_interface_row.button
        card.add_row(self.csr_groupBox)
        card.add_row(self.csr_theme_row)
        card.add_row(self.csr_show_minimize_row)
        card.add_row(self.csr_show_maximize_row)
        card.add_row(self.csr_direction_row)
        card.add_row(self.restart_interface_row)
        section.add_card(card)
        self.add_section(section)
