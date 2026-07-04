from gettext import gettext as _

from PyQt6.QtWidgets import QHBoxLayout, QStyle, QWidget

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


class LanguageDownloadSettingsView(SettingsPage):
    """Composable general settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Language and Download"),
            _("Manage interface language, downloads folder and spell checker."),
            parent,
        )
        self._setup_ui()
        self.configure_icons()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_language_section()
        self._setup_spellchecker_section()
        self._setup_flatpak_section()
        self._setup_downloads_section()

    def _setup_language_section(self):
        section = SettingsSection(
            _("Language"),
            _("Choose the interface language used by ZapZap."),
        )
        card = SettingsCard()
        row = SettingsSelectRow(
            _("Interface language"),
            _("The interface language is applied immediately."),
            [""],
        )
        self.interface_language_comboBox = row.combo
        self.interface_language_comboBox.setMinimumWidth(240)
        self.interface_language_comboBox.setMinimumContentsLength(18)
        card.add_row(row)
        section.add_card(card)
        self.add_section(section)

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
        self.add_section(section)

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
            _("Note: changing dictionaries may require restarting the browser "),
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
        self.add_section(section)

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
        self.add_section(self.flatpak_permissions_groupBox)

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
