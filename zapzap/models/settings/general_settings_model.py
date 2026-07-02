from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QLocale

from zapzap.services.SetupManager import SetupManager
from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.TranslationManager import TranslationManager


@dataclass(frozen=True)
class InterfaceLanguageOption:
    label: str
    value: str


class GeneralSettingsModel:
    """Model for general settings persistence and service access.

    This model hides SettingsManager keys and service-specific calls from
    the controller. The controller should use semantic properties/methods.
    """

    FLATPAK_OVERRIDE_COMMAND = (
        "flatpak override --user --filesystem=home com.rtosta.zapzap"
    )
    FLATSEAL_URL = "https://flathub.org/apps/com.github.tchx84.Flatseal"

    _SPELLCHECKERS = ("system/spellCheckers", True)
    _CONFIRM_ON_CLOSE = ("system/confirm_on_close", False)
    _QUIT_ON_CLOSE = ("system/quit_in_close", False)
    _START_BACKGROUND = ("system/start_background", False)
    _START_WITH_SYSTEM = ("system/start_system", False)
    _WAYLAND = ("system/wayland", False)
    _DONT_USE_NATIVE_DIALOG = ("system/DontUseNativeDialog", False)

    def _get_bool(self, setting: tuple[str, bool]) -> bool:
        key, default = setting
        return bool(SettingsManager.get(key, default))

    def _set_bool(self, setting: tuple[str, bool], value: bool) -> None:
        key, _default = setting
        SettingsManager.set(key, bool(value))

    @property
    def is_flatpak(self) -> bool:
        return bool(SetupManager._is_flatpak)

    @property
    def spellchecker_enabled(self) -> bool:
        return self._get_bool(self._SPELLCHECKERS)

    @spellchecker_enabled.setter
    def spellchecker_enabled(self, value: bool) -> None:
        self._set_bool(self._SPELLCHECKERS, value)

    @property
    def confirm_on_close(self) -> bool:
        return self._get_bool(self._CONFIRM_ON_CLOSE)

    @confirm_on_close.setter
    def confirm_on_close(self, value: bool) -> None:
        self._set_bool(self._CONFIRM_ON_CLOSE, value)

    @property
    def quit_on_close(self) -> bool:
        return self._get_bool(self._QUIT_ON_CLOSE)

    @quit_on_close.setter
    def quit_on_close(self, value: bool) -> None:
        self._set_bool(self._QUIT_ON_CLOSE, value)

    @property
    def start_in_background(self) -> bool:
        return self._get_bool(self._START_BACKGROUND)

    @start_in_background.setter
    def start_in_background(self, value: bool) -> None:
        self._set_bool(self._START_BACKGROUND, value)

    @property
    def start_with_system(self) -> bool:
        return self._get_bool(self._START_WITH_SYSTEM)

    @start_with_system.setter
    def start_with_system(self, value: bool) -> None:
        self._set_bool(self._START_WITH_SYSTEM, value)
        AutostartManager.create_desktop_file(bool(value))

    @property
    def wayland_enabled(self) -> bool:
        return self._get_bool(self._WAYLAND)

    @wayland_enabled.setter
    def wayland_enabled(self, value: bool) -> None:
        self._set_bool(self._WAYLAND, value)

    @property
    def dont_use_native_dialog(self) -> bool:
        return self._get_bool(self._DONT_USE_NATIVE_DIALOG)

    @dont_use_native_dialog.setter
    def dont_use_native_dialog(self, value: bool) -> None:
        self._set_bool(self._DONT_USE_NATIVE_DIALOG, value)

    @property
    def dictionaries_path(self) -> str:
        return DictionariesManager.get_path()

    @property
    def available_dictionaries(self) -> list[str]:
        return DictionariesManager.list()

    @property
    def current_dictionary(self) -> str:
        return DictionariesManager.get_current_dict()

    def set_dictionary_language(self, language: str) -> None:
        DictionariesManager.set_lang(language)

    def set_dictionaries_path(self, path: str) -> None:
        DictionariesManager.set_spell_folder(path)

    def restore_default_dictionaries_path(self) -> str:
        return DictionariesManager.restore_default_path()

    @property
    def download_path(self) -> str:
        return DownloadManager.get_path()

    def set_download_path(self, path: str) -> None:
        DownloadManager.set_path(path)

    def restore_default_download_path(self) -> str:
        DownloadManager.restore_path()
        return DownloadManager.get_path()

    @property
    def current_interface_language(self) -> str:
        return TranslationManager.get_current_language()

    def set_interface_language(self, language: str) -> None:
        TranslationManager.set_current_language(language)
        TranslationManager.apply()

    def interface_language_options(self, system_default_label: str) -> list[InterfaceLanguageOption]:
        options = [
            InterfaceLanguageOption(
                label=system_default_label,
                value=TranslationManager.SYSTEM_LANGUAGE,
            )
        ]

        for language in TranslationManager.list_available_languages():
            options.append(
                InterfaceLanguageOption(
                    label=self.language_label(language),
                    value=language,
                )
            )

        return options

    @staticmethod
    def language_label(language: str) -> str:
        locale = QLocale(language)
        language_name = QLocale.languageToString(locale.language())
        territory_name = QLocale.territoryToString(locale.territory())

        if territory_name:
            return f"{language_name} ({territory_name}) - {language}"

        return f"{language_name} - {language}"