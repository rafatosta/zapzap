from gettext import gettext as _

from PyQt6.QtCore import Qt

from zapzap.core.config.settings.system import DisplayBackend
from zapzap.core.environment.setup_manager import SetupManager

from zapzap.ui.components import (
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
        card.add_group(
            self.close_behavior_row,
            (self.btn_confirm_in_close_row,),
        )
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
            self.display_backend_row = SettingsSelectRow(
                _("Display backend"),
                _(
                    "Automatic is recommended and uses the native backend "
                    "for the current session. X11 is available as a "
                    "compatibility fallback."
                ),
                [""],
            )
            self.display_backend = self.display_backend_row.combo
            self.display_backend.clear()
            backend_options = (
                (
                    _("Automatic"),
                    DisplayBackend.AUTO.value,
                    _(
                        "Recommended. Use Wayland in Wayland sessions and "
                        "X11 in X11 sessions."
                    ),
                ),
                (
                    _("Wayland"),
                    DisplayBackend.WAYLAND.value,
                    _("Force the native Wayland backend."),
                ),
                (
                    _("X11 / XWayland"),
                    DisplayBackend.XCB.value,
                    _(
                        "Use the X11 backend. In Wayland sessions, this runs "
                        "through XWayland."
                    ),
                ),
            )
            for label, value, tooltip in backend_options:
                self.display_backend.addItem(label, value)
                self.display_backend.setItemData(
                    self.display_backend.count() - 1,
                    tooltip,
                    Qt.ItemDataRole.ToolTipRole,
                )
            self._configure_accessibility(
                self.display_backend_row,
                self.display_backend,
                description=_(
                    "Choose the Qt display backend. Changes require restart."
                ),
            )
            card.add_row(self.display_backend_row)

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
