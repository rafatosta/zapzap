"""User interface for the general settings page."""

from gettext import gettext as _

from PyQt6.QtWidgets import QHBoxLayout, QStyle, QVBoxLayout, QWidget

from zapzap.views.components import Button, LineEdit

from zapzap.views.settings_components import (
    SettingsActionRow,
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsPathRow,
    SettingsSection,
    SettingsSelectRow,
    SettingsSwitchRow,
)


class SystemStartupSettingsView(QWidget):
    """Composable general settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.configure_icons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(
            _("General"),
            _("Manage language, startup, downloads, spell checking, and Linux integration."),
            self,
        )
        layout.addWidget(self.page)

        self._setup_language_section()
        self._setup_startup_section()
        self._setup_window_behavior_section()
        self._setup_linux_section()
        self._setup_downloads_section()
        self._setup_spellchecker_section()
        self._setup_flatpak_section()
        self.page.add_stretch()

    def _setup_language_section(self):
        section = SettingsSection(
            _("Language"),
            _("Choose the interface language used by ZapZap."),
        )
        card = SettingsCard()
        row = SettingsSelectRow(
            _("Interface language"),
            _("The interface language is applied immediately."),
        )
        self.interface_language_comboBox = row.combo
        card.add_row(row)
        section.add_card(card)
        self.page.add_section(section)

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
        self.page.add_section(section)

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
        self.page.add_section(section)

    def _setup_linux_section(self):
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
        self.page.add_section(section)

    def _setup_downloads_section(self):
        section = SettingsSection(
            _("Downloads"),
            _("Choose where downloaded files are saved."),
        )
        card = SettingsCard()
        row = SettingsPathRow(
            _("Download directory"),
            _("Set a custom folder or restore the default download location."),
            button_text="",
        )
        self.download_path = row.line_edit
        self.download_path.setReadOnly(True)
        self.btn_path_download = row.button
        self.btn_restore_path_download = Button("")
        row.control.layout().addWidget(self.btn_restore_path_download)
        card.add_row(row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_spellchecker_section(self):
        section = SettingsSection(
            _("Spell checker"),
            _("Select compiled dictionaries and where ZapZap should look for them."),
        )
        card = SettingsCard()
        self.spellchecker_groupBox = SettingsSwitchRow(
            _("Enable spell checker"),
            _("Use Qt WebEngine spell checking with the selected dictionary."),
        )
        lang_row = SettingsSelectRow(
            _("Dictionary language"),
            _("Recognizes only compiled dictionaries (.bdic)."),
        )
        self.spell_comboBox = lang_row.combo
        path_row = SettingsPathRow(
            _("Dictionary directory"),
            _("Note: changing dictionaries may require restarting the browser page."),
            button_text="",
        )
        self.dic_path = path_row.line_edit
        self.dic_path.setReadOnly(True)
        self.btn_path_spell = path_row.button
        self.btn_default_path_spell = Button("")
        path_row.control.layout().addWidget(self.btn_default_path_spell)
        card.add_row(self.spellchecker_groupBox)
        card.add_row(lang_row)
        card.add_row(path_row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_flatpak_section(self):
        self.flatpak_permissions_groupBox = SettingsSection(
            _("Flatpak permissions"),
            _("Grant filesystem access if downloads, imports, or dictionaries cannot reach folders outside the sandbox."),
        )
        card = SettingsCard()
        card.add_row(SettingsInfoBox(_(
            "Flatpak sandbox: if file access fails, grant folder permissions using Flatseal or flatpak override."
        ), "warning"))
        command_row = QWidget()
        command_layout = QHBoxLayout(command_row)
        command_layout.setContentsMargins(0, 8, 0, 8)
        self.flatpak_command_input = LineEdit()
        self.flatpak_command_input.setReadOnly(True)
        self.flatpak_command_input.setToolTip(
            _("Select and copy this command in your terminal")
        )
        self.btn_copy_flatpak_command = Button(_("Copy"))
        command_layout.addWidget(self.flatpak_command_input, 1)
        command_layout.addWidget(self.btn_copy_flatpak_command)
        self.btn_open_flatseal = SettingsActionRow(
            _("Flatseal"),
            _("Flatseal is a graphical utility to review and modify permissions from your Flatpak applications."),
            _("Install Flatseal on Linux | Flathub"),
        )
        card.add_row(command_row)
        card.add_row(self.btn_open_flatseal)
        self.btn_open_flatseal = self.btn_open_flatseal.button
        self.flatpak_permissions_groupBox.add_card(card)
        self.page.add_section(self.flatpak_permissions_groupBox)

    def configure_icons(self):
        self.btn_path_download.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        )
        self.btn_restore_path_download.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)
        )
        self.btn_path_spell.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        )
        self.btn_default_path_spell.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)
        )

    def configure_flatpak(self, is_flatpak):
        self.flatpak_permissions_groupBox.setVisible(is_flatpak)
        self.btn_wayland.setDisabled(is_flatpak)
        if is_flatpak:
            self.btn_wayland.setToolTip(
                _("Use Flatseal to change this mode of execution")
            )