from gettext import gettext as _

from PyQt6.QtCore import Qt

from zapzap.core.environment.setup_manager import SetupManager

from zapzap.features.settings.components import (
    SettingsBadge,
    SettingsCard,
    SettingsPage,
    SettingsSection,
    SettingsSelectRow,
    SettingsSwitchRow,
)


class SystemStartupSettingsView(SettingsPage):
    """Composable general settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("System and startup"),
            _(
                "Configure how ZapZap starts, behaves in the system, "
                "and integrates with Linux."
            ),
            parent,
        )
        self.setObjectName("SystemStartupSettingsView")
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_startup_section()
        self._setup_window_behavior_section()
        self._setup_linux_section()

    def _setup_startup_section(self):
        section = SettingsSection(
            _("Startup"),
            _("Define how ZapZap behaves when your session starts."),
        )
        card = SettingsCard()
        self.btn_start_system_row = SettingsSwitchRow(
            _("Start with the system"),
            _("Open ZapZap automatically when the session starts."),
        )
        self.btn_start_background_row = SettingsSwitchRow(
            _("Start in the background"),
            _("Open without showing the main window."),
        )
        self.btn_start_system = self.btn_start_system_row.checkbox
        self.btn_start_background = self.btn_start_background_row.checkbox
        self._configure_accessibility(self.btn_start_system_row)
        self._configure_accessibility(self.btn_start_background_row)
        card.add_row(self.btn_start_system_row)
        card.add_row(self.btn_start_background_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_window_behavior_section(self):
        section = SettingsSection(
            _("Window"),
            _("Define what happens when the main window is closed."),
        )
        card = SettingsCard()
        self.close_behavior_row = SettingsSelectRow(
            _("Close behavior"),
            _(
                "Choose whether ZapZap continues in the background or quits."
            ),
            [""]
        )
        self.close_behavior = self.close_behavior_row.combo
        self.close_behavior.clear()
        self.close_behavior.addItem(
            _("Continue in the background"),
            "keep_running",
        )
        self.close_behavior.addItem(
            _("Quit ZapZap"),
            "quit_application",
        )
        self.close_behavior.setCurrentIndex(
            self.close_behavior.findData("keep_running")
        )
        self.btn_confirm_in_close_row = SettingsSwitchRow(
            _("Confirm before quitting"),
            _("Ask for confirmation before completely closing ZapZap."),
        )
        self.btn_confirm_in_close = self.btn_confirm_in_close_row.checkbox
        self._configure_accessibility(
            self.close_behavior_row,
            self.close_behavior,
            _(
                "Choose whether ZapZap continues in the background or quits "
                "when the window is closed."
            ),
        )
        self._configure_accessibility(self.btn_confirm_in_close_row)
        card.add_row(self.close_behavior_row)
        card.add_row(self.btn_confirm_in_close_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_linux_section(self):
        section = SettingsSection(
            _("Linux integration"),
            _("Settings related to the desktop environment and platform."),
        )
        card = SettingsCard()
        self.native_file_dialogs_row = SettingsSwitchRow(
            _("System file dialogs"),
            _("Use the file picker provided by the desktop environment."),
        )
        self.native_file_dialogs = self.native_file_dialogs_row.checkbox
        # Compatibility aliases for code that still refers to the persisted
        # setting's historical, negative name.
        self.dontUseNativeDialog_row = self.native_file_dialogs_row
        self.dontUseNativeDialog = self.native_file_dialogs
        self._configure_accessibility(self.native_file_dialogs_row)
        card.add_row(self.native_file_dialogs_row)

        if not SetupManager._is_flatpak:
            self.btn_wayland_row = SettingsSwitchRow(
                _("Run natively on Wayland"),
                _("Use the Wayland backend when available."),
            )
            self.btn_wayland = self.btn_wayland_row.checkbox
            self._configure_accessibility(
                self.btn_wayland_row,
                description=_(
                    "Use the Wayland backend when available. Requires restart."
                ),
            )
            self.wayland_restart_badge = SettingsBadge(
                _("Requires restart"),
                parent=self.btn_wayland_row,
            )
            self.wayland_restart_badge.setAccessibleName(
                _("Wayland changes require restart")
            )
            card.add_row(self.btn_wayland_row)
            text_column = self.btn_wayland_row.layout().itemAt(0).widget()
            text_column.layout().addWidget(
                self.wayland_restart_badge,
                0,
                Qt.AlignmentFlag.AlignLeft,
            )

        section.add_card(card)
        self.add_section(section)

    @staticmethod
    def _configure_accessibility(row, control=None, description=None):
        """Associate each visible setting label with its interactive control."""
        control = control or row.checkbox
        control.setAccessibleName(row.title_label.text())
        if description is None and row.description_label is not None:
            description = row.description_label.text()
        control.setAccessibleDescription(description or "")
        row.title_label.setBuddy(control)
