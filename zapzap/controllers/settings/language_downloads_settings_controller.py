"""Controller for the general settings page."""

from gettext import gettext as _

from PyQt6.QtCore import QLocale, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.models.settings import LanguageDownloadSettingsModel
from zapzap.views.settings import LanguageDownloadSettingsView


class LanguageDownloadSettingsController(LanguageDownloadSettingsView):
    """Coordinates general settings state and actions for the """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = LanguageDownloadSettingsModel()
        self._configure_ui()
        self._load_settings()
        self._connect_signals()

    def _configure_ui(self):
        self.configure_flatpak(self.model.is_flatpak())

    def _load_settings(self):
        self.dic_path.setText(self.model.get_dictionaries_path())
        self.spellchecker_groupBox.checkbox.setChecked(
            self.model.get_setting("system/spellCheckers", True)
        )

        self.spell_comboBox.clear()
        print(self.model.list_dictionaries())
        self.spell_comboBox.addItems(self.model.list_dictionaries())
        self.spell_comboBox.setCurrentText(self.model.get_current_dictionary())

        self.download_path.setText(self.model.get_download_path())

        self._load_interface_languages()
        self.flatpak_command_input.setText(self.model.FLATPAK_OVERRIDE_COMMAND)

    def _connect_signals(self):
        self.spellchecker_groupBox.checkbox.toggled.connect(
            self._handle_toggled_spellcheck
        )
        self.interface_language_comboBox.currentIndexChanged.connect(
            self._handle_interface_language
        )
        self.spell_comboBox.textActivated.connect(self._handle_spellcheck)
        self.btn_path_spell.clicked.connect(self._handle_path_spell)
        self.btn_default_path_spell.clicked.connect(
            self._handle_default_folder_spell
        )
        self.btn_path_download.clicked.connect(self._handle_path_download)
        self.btn_restore_path_download.clicked.connect(
            self._handle_restore_path_download
        )
        
        self.btn_copy_flatpak_command.clicked.connect(
            lambda: QApplication.clipboard().setText(
                self.model.FLATPAK_OVERRIDE_COMMAND
            )
        )
        self.btn_open_flatseal.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
            )
        )

    def _load_interface_languages(self):
        combo = self.interface_language_comboBox
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(_("System default"), "system")

        for language in self.model.list_available_languages():
            combo.addItem(self._language_label(language), language)

        current_language = self.model.get_current_language()
        index = combo.findData(current_language)
        if index < 0:
            index = 0
        combo.setCurrentIndex(index)
        combo.blockSignals(False)

    def _language_label(self, language):
        locale = QLocale(language)
        language_name = QLocale.languageToString(locale.language())
        territory_name = QLocale.territoryToString(locale.territory())

        if territory_name:
            return f"{language_name} ({territory_name}) - {language}"
        return f"{language_name} - {language}"

    def _handle_interface_language(self, *_args):
        language = self.interface_language_comboBox.currentData()
        self.model.set_current_language(language)
        self.model.apply_translation()
        self._retranslate_application()

    def _retranslate_application(self):
        app = QApplication.instance()
        for widget in app.allWidgets():
            retranslate = getattr(widget, "retranslateUi", None)
            if callable(retranslate):
                retranslate(widget)

        self._load_interface_languages()

    def _handle_toggled_spellcheck(self, toggled):
        self.model.set_setting("system/spellCheckers", toggled)
        self._update_browser_spellcheck()

    def _handle_spellcheck(self, language):
        self.model.set_dictionary_language(language)
        self._update_browser_spellcheck()

    def _handle_path_spell(self):
        new_path = self.model.open_folder_dialog(self)
        if new_path:
            self.dic_path.setText(new_path)
            self.model.set_dictionary_path(new_path)
            self._load_settings()
            self._update_browser_spellcheck()

    def _handle_autostart(self):
        self.model.set_autostart(self.btn_start_system.isChecked())

    def _handle_default_folder_spell(self):
        new_path = self.model.restore_dictionary_path()
        self.dic_path.setText(new_path)
        self._load_settings()
        self._update_browser_spellcheck()

    def _update_browser_spellcheck(self):
        QApplication.instance().getWindow().browser.update_spellcheck()

    def _handle_path_download(self):
        new_path = self.model.open_folder_dialog(self)
        if new_path:
            self.model.set_download_path(new_path)
            self.download_path.setText(self.model.get_download_path())

    def _handle_restore_path_download(self):
        self.download_path.setText(self.model.restore_download_path())
