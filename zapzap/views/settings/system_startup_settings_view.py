from gettext import gettext as _

from zapzap.core.environment.SetupManager import SetupManager

from zapzap.views.settings_components import (
    SettingsCard,
    SettingsPage,
    SettingsSection,
    SettingsSwitchRow,
)


class SystemStartupSettingsView(SettingsPage):
    """Composable general settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("General"),
            _("Manage language, startup, downloads, spell checking, and Linux integration."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_startup_section()
        self._setup_window_behavior_section()
        self._setup_linux_section()

    def _setup_startup_section(self):
        section = SettingsSection(
            _("Startup"),
            _("Control how ZapZap behaves when your desktop session starts."),
        )
        card = SettingsCard()
        self.btn_start_background_row = SettingsSwitchRow(
            _("Start minimized"),
            _("Open ZapZap in the background instead of showing the main window."),
        )
        self.btn_start_system_row = SettingsSwitchRow(
            _("Start with the system"),
            _("Create or remove the desktop autostart entry."),
        )
        self.btn_start_background = self.btn_start_background_row.checkbox
        self.btn_start_system = self.btn_start_system_row.checkbox
        card.add_row(self.btn_start_background_row)
        card.add_row(self.btn_start_system_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_window_behavior_section(self):
        section = SettingsSection(
            _("Window behavior"),
            _("Configure close behavior and native dialogs."),
        )
        card = SettingsCard()
        self.btn_confirm_in_close_row = SettingsSwitchRow(
            _("Confirm before closing the window"),
            _("Ask for confirmation before closing ZapZap."),
        )
        self.btn_quit_in_close_row = SettingsSwitchRow(
            _("Close when closing the window"),
            _("Quit the application when the main window is closed."),
        )
        self.dontUseNativeDialog_row = SettingsSwitchRow(
            _("Don't use a platform-native file dialog"),
            _("Use Qt file dialogs instead of the desktop portal or native picker."),
        )
        self.btn_confirm_in_close = self.btn_confirm_in_close_row.checkbox
        self.btn_quit_in_close = self.btn_quit_in_close_row.checkbox
        self.dontUseNativeDialog = self.dontUseNativeDialog_row.checkbox
        card.add_row(self.btn_confirm_in_close_row)
        card.add_row(self.btn_quit_in_close_row)
        card.add_row(self.dontUseNativeDialog_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_linux_section(self):

        if not SetupManager._is_flatpak:
            section = SettingsSection(
                _("Linux integration"),
                _("Options that affect how ZapZap integrates with Linux desktop sessions."),
            )
            card = SettingsCard()
            self.btn_wayland_row = SettingsSwitchRow(
                _("Wayland window system"),
                _("Enable Wayland-specific execution mode. A restart may be required."),
            )
            self.btn_wayland = self.btn_wayland_row.checkbox
            card.add_row(self.btn_wayland_row)
            section.add_card(card)
            self.add_section(section)
