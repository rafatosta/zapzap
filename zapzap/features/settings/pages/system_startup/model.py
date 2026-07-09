"""Data access for the general settings page."""

from zapzap.features.startup.autostart_manager import AutostartManager
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.i18n.translation_manager import TranslationManager


class SystemStartupSettingsModel:
    """Facade over services used by the general settings controller."""

    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    def is_flatpak(self):
        return SetupManager._is_flatpak

    _WAYLAND = ("system/wayland", False)
    _CONFIRM_ON_CLOSE = ("system/confirm_on_close", False)
    _QUIT_IN_CLOSE = ("system/quit_in_close", False)
    _START_BACKGROUND = ("system/start_background", False)
    _START_SYSTEM = ("system/start_system", False)
    _DONT_USE_NATIVE_DIALOG = ("system/DontUseNativeDialog", False)

    @staticmethod
    def _get_bool(setting: tuple[str, bool]) -> bool:
        key, default = setting
        return bool(SettingsManager.get(key, default))

    @staticmethod
    def _set_bool(setting: tuple[str, bool], value: bool) -> None:
        key, _default = setting
        SettingsManager.set(key, bool(value))

    @property
    def wayland_enabled(self) -> bool:
        return self._get_bool(self._WAYLAND)

    @wayland_enabled.setter
    def wayland_enabled(self, value: bool) -> None:
        self._set_bool(self._WAYLAND, value)

    @property
    def confirm_on_close(self) -> bool:
        return self._get_bool(self._CONFIRM_ON_CLOSE)

    @confirm_on_close.setter
    def confirm_on_close(self, value: bool) -> None:
        self._set_bool(self._CONFIRM_ON_CLOSE, value)

    @property
    def quit_on_close(self) -> bool:
        return self._get_bool(self._QUIT_IN_CLOSE)

    @quit_on_close.setter
    def quit_on_close(self, value: bool) -> None:
        self._set_bool(self._QUIT_IN_CLOSE, value)

    @property
    def start_in_background(self) -> bool:
        return self._get_bool(self._START_BACKGROUND)

    @start_in_background.setter
    def start_in_background(self, value: bool) -> None:
        self._set_bool(self._START_BACKGROUND, value)

    @property
    def start_with_system(self) -> bool:
        return self._get_bool(self._START_SYSTEM)

    @property
    def dont_use_native_dialog(self) -> bool:
        return self._get_bool(self._DONT_USE_NATIVE_DIALOG)

    @dont_use_native_dialog.setter
    def dont_use_native_dialog(self, value: bool) -> None:
        self._set_bool(self._DONT_USE_NATIVE_DIALOG, value)

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
        self._set_bool(self._START_SYSTEM, enabled)
        AutostartManager.create_desktop_file(enabled)

    def list_available_languages(self):
        return TranslationManager.list_available_languages()

    def get_current_language(self):
        return TranslationManager.get_current_language()

    def set_current_language(self, language):
        TranslationManager.set_current_language(language)

    def apply_translation(self):
        TranslationManager.apply()
