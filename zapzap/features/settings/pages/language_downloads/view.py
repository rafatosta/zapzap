from gettext import gettext as _

from zapzap.ui.primitives import Button

from zapzap.ui.components import (
    SettingsCard,
    SettingsActionRow,
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
        self.add_stretch()

    def _setup_ui(self):
        self._setup_language_section()
        self._setup_spellchecker_section()
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
            button_text=_("Define"),
        )
        self.download_path = row.line_edit
        self.download_path.setReadOnly(True)
        self.btn_path_download = row.button
        self.btn_restore_path_download = Button(
            _("Restore"), variant=Button.WARNING)
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
        self.spell_languages_row = SettingsActionRow(
            _("Spell checker languages"),
            _("No dictionary available"),
            button_text=_("Select…"),
        )
        self.btn_select_spell_languages = self.spell_languages_row.button
        self.btn_select_spell_languages.setAccessibleName(
            _("Select spell checker languages"))
        self.manage_dictionaries_row = SettingsActionRow(
            _("Dictionary files"),
            _("Install, remove, or import dictionaries in ZapZap storage."),
            button_text=_("Manage…"),
        )
        self.btn_manage_dictionaries = self.manage_dictionaries_row.button
        self.btn_manage_dictionaries.setAccessibleName(_("Manage dictionaries"))
        self.btn_manage_dictionaries.setAccessibleDescription(
            _("Open the Qt WebEngine dictionary manager."))
        self.spellchecker_options_group = card.add_group(
            self.spellchecker_groupBox,
            (self.spell_languages_row, self.manage_dictionaries_row),
        )
        section.add_card(card)
        self.add_section(section)
