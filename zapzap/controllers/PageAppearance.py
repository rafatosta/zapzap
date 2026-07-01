from gettext import gettext as _

from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QRadioButton, QWidget

from zapzap.resources.CSRButtonThemeProvider import CSRButtonThemeProvider
from zapzap.resources.TrayIcon import TrayIcon
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager
from zapzap.views.settings_components import SettingsCard, SettingsPage, SettingsSection, SettingsSelectRow, SettingsSwitchRow


class PageAppearance(QWidget):
    """Classe para gerenciar a página de configurações de aparência."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()
        self._configure_signals()

    def _setup_ui(self):
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(_("Appearance"), _("Adjust interface chrome, theme, tray icon, grid view, and window decorations."), self)
        layout.addWidget(self.page)

        interface = SettingsSection(_("Interface"), _("Show or hide primary application chrome."))
        interface_card = SettingsCard()
        self.browser_sidebar_row = SettingsSwitchRow(_("Browser sidebar"), _("Show account navigation in the browser shell."))
        self.mainwindow_menu_row = SettingsSwitchRow(_("Menu bar"), _("Show the main window menu bar."))
        self.scale_row = SettingsSelectRow(_("Interface scale"), _("Scale the interface for high-DPI or accessibility needs."), ["50 %", "75 %", "100 %", "125 %", "150 %", "175 %", "200 %"])
        self.browser_sidebar = self.browser_sidebar_row.checkbox
        self.mainwindow_menu = self.mainwindow_menu_row.checkbox
        self.scaleComboBox = self.scale_row.combo
        interface_card.add_row(self.browser_sidebar_row)
        interface_card.add_row(self.mainwindow_menu_row)
        interface_card.add_row(self.scale_row)
        interface.add_card(interface_card)
        self.page.add_section(interface)

        theme = SettingsSection(_("Theme"), _("Choose the visual theme."))
        theme_card = SettingsCard()
        self.theme_auto_radioButton = QRadioButton(_("Automatic"))
        self.theme_light_radioButton = QRadioButton(_("Light"))
        self.theme_dark_radioButton = QRadioButton(_("Dark"))
        theme_row = QWidget()
        theme_layout = QHBoxLayout(theme_row)
        theme_layout.setContentsMargins(0, 8, 0, 8)
        theme_layout.addWidget(self.theme_auto_radioButton)
        theme_layout.addWidget(self.theme_light_radioButton)
        theme_layout.addWidget(self.theme_dark_radioButton)
        theme_layout.addStretch(1)
        theme_card.add_row(theme_row)
        theme.add_card(theme_card)
        self.page.add_section(theme)

        tray = SettingsSection(_("Tray icon"), _("Control tray icon visibility, style, and unread counter."))
        tray_card = SettingsCard()
        self.tray_groupBox = SettingsSwitchRow(_("Enable tray icon"), _("Show ZapZap in the system tray."))
        self.notificationCounter_row = SettingsSwitchRow(_("Notification counter"), _("Show unread notifications on the tray icon."))
        self.notificationCounter = self.notificationCounter_row.checkbox
        self.tray_default_radioButton = QRadioButton(_("Default"))
        self.tray_slight_radioButton = QRadioButton(_("Symbolic light"))
        self.tray_sdark_radioButton = QRadioButton(_("Symbolic dark"))
        tray_modes = QWidget()
        tray_layout = QHBoxLayout(tray_modes)
        tray_layout.setContentsMargins(0, 8, 0, 8)
        for radio in (self.tray_default_radioButton, self.tray_slight_radioButton, self.tray_sdark_radioButton):
            tray_layout.addWidget(radio)
        tray_layout.addStretch(1)
        tray_card.add_row(self.tray_groupBox)
        tray_card.add_row(self.notificationCounter_row)
        tray_card.add_row(tray_modes)
        tray.add_card(tray_card)
        self.page.add_section(tray)

        grid = SettingsSection(_("Grid view"), _("Choose how many columns are used by grid view."))
        grid_card = SettingsCard()
        self.grid_row = SettingsSelectRow(_("Grid columns"), _("Number of account columns in grid view."), ["2", "3", "4"])
        self.gridColsComboBox = self.grid_row.combo
        grid_card.add_row(self.grid_row)
        grid.add_card(grid_card)
        self.page.add_section(grid)

        csr = SettingsSection(_("Custom window decoration"), _("Configure client-side rendering window buttons."))
        csr_card = SettingsCard()
        self.csr_groupBox = SettingsSwitchRow(_("Use custom window decoration"), _("Draw ZapZap window controls instead of native ones."))
        self.csr_theme_comboBox = QComboBox()
        self.csr_theme_row = SettingsSelectRow(_("Button theme"), _("Theme used by custom window buttons."))
        self.csr_theme_comboBox = self.csr_theme_row.combo
        self.csr_show_minimize_row = SettingsSwitchRow(_("Show minimize button"))
        self.csr_show_maximize_row = SettingsSwitchRow(_("Show maximize button"))
        self.csr_show_minimize_checkBox = self.csr_show_minimize_row.checkbox
        self.csr_show_maximize_checkBox = self.csr_show_maximize_row.checkbox
        self.csr_direction_comboBox = QComboBox()
        self.csr_direction_comboBox.addItems(["right", "left"])
        self.csr_direction_row = SettingsSelectRow(_("Button direction"), _("Place window buttons on the right or left."))
        self.csr_direction_row.combo.addItems(["right", "left"])
        self.csr_direction_comboBox = self.csr_direction_row.combo
        csr_card.add_row(self.csr_groupBox)
        csr_card.add_row(self.csr_theme_row)
        csr_card.add_row(self.csr_show_minimize_row)
        csr_card.add_row(self.csr_show_maximize_row)
        csr_card.add_row(self.csr_direction_row)
        csr.add_card(csr_card)
        self.page.add_section(csr)
        self.page.add_stretch()

    def _load_settings(self):
        self.browser_sidebar.setChecked(SettingsManager.get("system/sidebar", True))
        self.mainwindow_menu.setChecked(SettingsManager.get("system/menubar", True))
        self.scaleComboBox.setCurrentText(f"{SettingsManager.get('system/scale', 100)} %")
        self.tray_groupBox.checkbox.setChecked(SettingsManager.get("system/tray_icon", True))
        self.notificationCounter.setChecked(SettingsManager.get("system/notificationCounter", False))
        self.csr_groupBox.checkbox.setChecked(SettingsManager.get("system/csr", False))
        self.csr_theme_comboBox.clear()
        self.csr_theme_comboBox.addItems(CSRButtonThemeProvider.available_theme_names())
        csr_theme = str(SettingsManager.get("system/csr_button_theme", "default")).lower()
        theme_index = self.csr_theme_comboBox.findText(csr_theme)
        self.csr_theme_comboBox.setCurrentIndex(theme_index if theme_index >= 0 else 0)
        self.csr_show_minimize_checkBox.setChecked(SettingsManager.get("system/csr_show_minimize_button", True))
        self.csr_show_maximize_checkBox.setChecked(SettingsManager.get("system/csr_show_maximize_button", True))
        csr_direction = str(SettingsManager.get("system/csr_buttons_direction", "right")).strip().lower()
        self.csr_direction_comboBox.setCurrentIndex(1 if csr_direction == "left" else 0)

        self._set_selected_radio(SettingsManager.get("system/theme", ThemeManager.Type.Auto.value), {
            ThemeManager.Type.Auto.value: self.theme_auto_radioButton,
            ThemeManager.Type.Light.value: self.theme_light_radioButton,
            ThemeManager.Type.Dark.value: self.theme_dark_radioButton,
        })
        self.gridColsComboBox.setCurrentText(str(SettingsManager.get("system/grid_cols", 2)))
        self._set_selected_radio(SettingsManager.get("system/tray_theme", TrayIcon.Type.Default.value), {
            TrayIcon.Type.Default.value: self.tray_default_radioButton,
            TrayIcon.Type.SLight.value: self.tray_slight_radioButton,
            TrayIcon.Type.SDark.value: self.tray_sdark_radioButton,
        })

    def _setup_grid_options(self):
        pass

    def _handle_grid_cols(self, text):
        SettingsManager.set("system/grid_cols", int(text))

    def _configure_signals(self):
        self.browser_sidebar.clicked.connect(self._handle_sidebar)
        self.mainwindow_menu.clicked.connect(self._handle_menubar)
        self.scaleComboBox.currentTextChanged.connect(self._handle_scale)
        self.tray_groupBox.checkbox.toggled.connect(SysTrayManager.set_state)
        self.notificationCounter.clicked.connect(self._handle_remove_notification_indicator)
        self.gridColsComboBox.currentTextChanged.connect(self._handle_grid_cols)
        self.tray_default_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_slight_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_sdark_radioButton.toggled.connect(self._handle_tray_mode)
        self.theme_auto_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_light_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_dark_radioButton.toggled.connect(self._handle_theme_mode)
        self.csr_groupBox.checkbox.toggled.connect(self._handle_csr_enabled)
        self.csr_theme_comboBox.currentTextChanged.connect(self._handle_csr_theme)
        self.csr_show_minimize_checkBox.toggled.connect(self._handle_csr_show_minimize)
        self.csr_show_maximize_checkBox.toggled.connect(self._handle_csr_show_maximize)
        self.csr_direction_comboBox.currentTextChanged.connect(self._handle_csr_direction)

    @staticmethod
    def _set_selected_radio(selected_value, radio_map):
        radio_button = radio_map.get(selected_value)
        if radio_button:
            radio_button.setChecked(True)

    def _handle_sidebar(self):
        QApplication.instance().getWindow().set_sidebar_visible(self.browser_sidebar.isChecked())

    def _handle_menubar(self):
        SettingsManager.set("system/menubar", self.mainwindow_menu.isChecked())
        QApplication.instance().getWindow().settings_menubar()

    def _handle_scale(self, text):
        SettingsManager.set("system/scale", ''.join(filter(str.isdigit, text)))

    def _handle_tray_mode(self):
        selected_tray_mode = self._get_selected_radio({
            self.tray_default_radioButton: TrayIcon.Type.Default,
            self.tray_slight_radioButton: TrayIcon.Type.SLight,
            self.tray_sdark_radioButton: TrayIcon.Type.SDark,
        })
        if selected_tray_mode:
            SysTrayManager.set_theme(selected_tray_mode)

    def _handle_theme_mode(self):
        selected_theme_mode = self._get_selected_radio({
            self.theme_auto_radioButton: ThemeManager.Type.Auto,
            self.theme_light_radioButton: ThemeManager.Type.Light,
            self.theme_dark_radioButton: ThemeManager.Type.Dark,
        })
        if selected_theme_mode:
            ThemeManager.set_theme(selected_theme_mode)

    @staticmethod
    def _get_selected_radio(radio_map):
        for radio_button, value in radio_map.items():
            if radio_button.isChecked():
                return value
        return None

    def _handle_remove_notification_indicator(self):
        SettingsManager.set("system/notificationCounter", self.notificationCounter.isChecked())
        SysTrayManager.refresh()

    def _refresh_csr_buttons(self):
        window = QApplication.instance().getWindow()
        if getattr(window, "is_csr_wrapper", False):
            window.refresh_csr_button_preferences()

    def _handle_csr_enabled(self, enabled):
        SettingsManager.set("system/csr", enabled)

    def _handle_csr_theme(self, theme_name):
        SettingsManager.set("system/csr_button_theme", theme_name)
        self._refresh_csr_buttons()

    def _handle_csr_show_minimize(self, enabled):
        SettingsManager.set("system/csr_show_minimize_button", enabled)
        self._refresh_csr_buttons()

    def _handle_csr_show_maximize(self, enabled):
        SettingsManager.set("system/csr_show_maximize_button", enabled)
        self._refresh_csr_buttons()

    def _handle_csr_direction(self, direction_label):
        direction = "left" if direction_label.strip().lower() == "left" else "right"
        SettingsManager.set("system/csr_buttons_direction", direction)
        self._refresh_csr_buttons()
