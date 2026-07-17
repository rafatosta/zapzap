"""Data access for the general settings page."""

from zapzap.features.startup.autostart_manager import AutostartManager
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.core.config.settings.spellcheck import SpellcheckSettings
from zapzap.core.config.settings.system import SystemSettings
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.i18n.translation_manager import TranslationManager


class LanguageDownloadSettingsModel:
    """Facade over services used by the general settings controller."""

    def is_flatpak(self):
        return SetupManager._is_flatpak

    def __init__(self):
        self._spellcheck_settings = SpellcheckSettings()
        self._system_settings = SystemSettings()

    @property
    def spellcheck_enabled(self):
        return self._spellcheck_settings.enabled

    @spellcheck_enabled.setter
    def spellcheck_enabled(self, value):
        self._spellcheck_settings.enabled = value

    def get_dictionaries_path(self):
        return DictionariesManager.get_path()

    def list_dictionaries(self):
        return DictionariesManager.list()

    def get_current_dictionary(self):
        return DictionariesManager.get_current_dict()

    def set_dictionary_language(self, language):
        DictionariesManager.set_lang(language)

    def set_dictionary_path(self, path):
        DictionariesManager.set_spell_folder(path)

    def restore_dictionary_path(self):
        return DictionariesManager.restore_default_path()

    def get_download_path(self):
        return DownloadManager.get_path()

    def set_download_path(self, path):
        DownloadManager.set_path(path)

    def restore_download_path(self):
        DownloadManager.restore_path()
        return DownloadManager.get_path()

    def open_folder_dialog(self, parent):
        return DownloadManager.open_folder_dialog(parent)

    def set_autostart(self, enabled):
        self._system_settings.start_with_system = enabled
        AutostartManager.create_desktop_file(enabled)

    def list_available_languages(self):
        return TranslationManager.list_available_languages()

    def get_current_language(self):
        return TranslationManager.get_current_language()

    def set_current_language(self, language):
        TranslationManager.set_current_language(language)

    def apply_translation(self):
        TranslationManager.apply()
