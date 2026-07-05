"""Data access for the general settings page."""

from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.core.config.SettingsManager import SettingsManager
from zapzap.core.environment.SetupManager import SetupManager
from zapzap.core.i18n.TranslationManager import TranslationManager


class LanguageDownloadSettingsModel:
    """Facade over services used by the general settings controller."""

    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    def is_flatpak(self):
        return SetupManager._is_flatpak

    def get_setting(self, key, default=None):
        return SettingsManager.get(key, default)

    def set_setting(self, key, value):
        SettingsManager.set(key, value)

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
        SettingsManager.set("system/start_system", enabled)
        AutostartManager.create_desktop_file(enabled)

    def list_available_languages(self):
        return TranslationManager.list_available_languages()

    def get_current_language(self):
        return TranslationManager.get_current_language()

    def set_current_language(self, language):
        TranslationManager.set_current_language(language)

    def apply_translation(self):
        TranslationManager.apply()
