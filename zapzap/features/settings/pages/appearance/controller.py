"""Controller for the appearance settings page."""

from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.pages.appearance.model import AppearanceSettingsModel
from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.settings.pages.appearance.view import AppearanceSettingsView


class AppearanceSettingsController(AppearanceSettingsView):
    """Coordinates appearance settings state and actions for the view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AppearanceSettingsModel()
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        self.browser_sidebar.setChecked(self.model.browser_sidebar_visible)
        self.mainwindow_menu.setChecked(self.model.menubar_visible)
        self.scaleComboBox.setCurrentText(f"{self.model.scale} %")
        self.tray_groupBox.checkbox.setChecked(self.model.tray_icon_enabled)
        self.notificationCounter.setChecked(
            self.model.notification_counter_enabled)
        self.gridColsComboBox.setCurrentText(str(self.model.grid_columns))

        self.csr_groupBox.checkbox.setChecked(self.model.csr_enabled)
        self._load_csr_button_themes()
        self.csr_show_minimize_checkBox.setChecked(
            self.model.csr_show_minimize_button
        )
        self.csr_show_maximize_checkBox.setChecked(
            self.model.csr_show_maximize_button
        )
        self.csr_direction_comboBox.setCurrentText(
            self.model.csr_buttons_direction)

        self._set_selected_radio(
            self.model.theme,
            {
                ThemeManager.Type.Auto.value: self.theme_auto_radioButton,
                ThemeManager.Type.Light.value: self.theme_light_radioButton,
                ThemeManager.Type.Dark.value: self.theme_dark_radioButton,
            },
        )
        self._set_selected_radio(
            self.model.tray_theme,
            {
                TrayIcon.Type.Default.value: self.tray_default_radioButton,
                TrayIcon.Type.SLight.value: self.tray_slight_radioButton,
                TrayIcon.Type.SDark.value: self.tray_sdark_radioButton,
            },
        )

    def _load_csr_button_themes(self):
        self.csr_theme_comboBox.blockSignals(True)
        self.csr_theme_comboBox.clear()
        self.csr_theme_comboBox.addItems(
            self.model.available_csr_button_themes())
        theme_index = self.csr_theme_comboBox.findText(
            self.model.csr_button_theme)
        self.csr_theme_comboBox.setCurrentIndex(
            theme_index if theme_index >= 0 else 0)
        self.csr_theme_comboBox.blockSignals(False)

    def _connect_signals(self):
        self.browser_sidebar.clicked.connect(self._handle_sidebar)
        self.mainwindow_menu.clicked.connect(self._handle_menubar)
        self.scaleComboBox.currentTextChanged.connect(self._handle_scale)
        self.tray_groupBox.checkbox.toggled.connect(self._handle_tray_enabled)
        self.notificationCounter.clicked.connect(
            self._handle_notification_counter)
        self.gridColsComboBox.currentTextChanged.connect(
            self._handle_grid_cols)
        self.tray_default_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_slight_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_sdark_radioButton.toggled.connect(self._handle_tray_mode)
        self.theme_auto_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_light_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_dark_radioButton.toggled.connect(self._handle_theme_mode)
        self.csr_groupBox.checkbox.toggled.connect(self._handle_csr_enabled)
        self.csr_theme_comboBox.currentTextChanged.connect(
            self._handle_csr_theme)
        self.csr_show_minimize_checkBox.toggled.connect(
            self._handle_csr_show_minimize
        )
        self.csr_show_maximize_checkBox.toggled.connect(
            self._handle_csr_show_maximize
        )
        self.csr_direction_comboBox.currentTextChanged.connect(
            self._handle_csr_direction
        )

    @staticmethod
    def _set_selected_radio(selected_value, radio_map):
        radio_button = radio_map.get(selected_value)
        if radio_button:
            radio_button.setChecked(True)

    @staticmethod
    def _get_selected_radio(radio_map):
        for radio_button, value in radio_map.items():
            if radio_button.isChecked():
                return value
        return None

    def _handle_sidebar(self):
        enabled = self.browser_sidebar.isChecked()
        self.model.browser_sidebar_visible = enabled
        QApplication.instance().getWindow().set_sidebar_visible(enabled)

    def _handle_menubar(self):
        self.model.menubar_visible = self.mainwindow_menu.isChecked()
        QApplication.instance().getWindow().settings_menubar()

    def _handle_scale(self, text):
        digits = "".join(filter(str.isdigit, text))
        if digits:
            self.model.scale = int(digits)

    def _handle_tray_enabled(self, enabled):
        self.model.tray_icon_enabled = enabled
        self.model.apply_tray_icon_enabled(enabled)

    def _handle_notification_counter(self):
        self.model.notification_counter_enabled = self.notificationCounter.isChecked()
        self.model.refresh_tray()

    def _handle_grid_cols(self, text):
        if text:
            self.model.grid_columns = int(text)

    def _handle_tray_mode(self):
        selected_tray_mode = self._get_selected_radio(
            {
                self.tray_default_radioButton: TrayIcon.Type.Default,
                self.tray_slight_radioButton: TrayIcon.Type.SLight,
                self.tray_sdark_radioButton: TrayIcon.Type.SDark,
            }
        )
        if selected_tray_mode:
            self.model.tray_theme = selected_tray_mode.value
            self.model.apply_tray_theme(selected_tray_mode)

    def _handle_theme_mode(self):
        selected_theme_mode = self._get_selected_radio(
            {
                self.theme_auto_radioButton: ThemeManager.Type.Auto,
                self.theme_light_radioButton: ThemeManager.Type.Light,
                self.theme_dark_radioButton: ThemeManager.Type.Dark,
            }
        )
        if selected_theme_mode:
            self.model.theme = selected_theme_mode.value
            self.model.apply_theme(selected_theme_mode)

    def _refresh_csr_buttons(self):
        window = QApplication.instance().getWindow()
        if getattr(window, "is_csr_wrapper", False):
            window.refresh_csr_button_preferences()

    def _handle_csr_enabled(self, enabled):
        self.model.csr_enabled = enabled

    def _handle_csr_theme(self, theme_name):
        self.model.csr_button_theme = theme_name
        self._refresh_csr_buttons()

    def _handle_csr_show_minimize(self, enabled):
        self.model.csr_show_minimize_button = enabled
        self._refresh_csr_buttons()

    def _handle_csr_show_maximize(self, enabled):
        self.model.csr_show_maximize_button = enabled
        self._refresh_csr_buttons()

    def _handle_csr_direction(self, direction_label):
        self.model.csr_buttons_direction = direction_label
        self._refresh_csr_buttons()
