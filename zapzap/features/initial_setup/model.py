"""Persistence facade for the initial setup flow."""

from __future__ import annotations

from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.features.permissions.permissions_manager import PermissionsManager
from zapzap.features.startup.autostart_manager import AutostartManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager


class InitialSetupModel:
    """Centralizes settings read/write operations used by onboarding."""

    COMPLETED_KEY = "onboarding/initial_setup_completed"

    @classmethod
    def is_completed(cls) -> bool:
        return bool(SettingsManager.get(cls.COMPLETED_KEY, False))

    @classmethod
    def mark_completed(cls) -> None:
        SettingsManager.set(cls.COMPLETED_KEY, True)

    def available_languages(self) -> list[str]:
        return TranslationManager.list_available_languages()

    def current_language(self) -> str:
        return TranslationManager.get_current_language()

    def set_language(self, language: str) -> None:
        TranslationManager.set_current_language(language)
        TranslationManager.apply()

    def current_theme(self) -> str:
        return str(SettingsManager.get("system/theme", ThemeManager.Type.Auto.value))

    def set_theme(self, theme: str) -> None:
        ThemeManager.set_theme(theme)

    def get_bool(self, key: str, default: bool = False) -> bool:
        return bool(SettingsManager.get(key, default))

    def set_bool(self, key: str, value: bool) -> None:
        SettingsManager.set(key, bool(value))

    def set_autostart(self, enabled: bool) -> None:
        SettingsManager.set("system/start_system", bool(enabled))
        AutostartManager.create_desktop_file(bool(enabled))

    def set_tray_icon(self, enabled: bool) -> None:
        SysTrayManager.set_state(bool(enabled))

    def refresh_tray(self) -> None:
        SysTrayManager.refresh()

    def download_path(self) -> str:
        return DownloadManager.get_path()

    def set_download_path(self, path: str) -> None:
        DownloadManager.set_path(path)

    def open_download_folder_dialog(self, parent) -> str:
        return DownloadManager.open_folder_dialog(parent)

    def dictionaries(self) -> list[str]:
        return DictionariesManager.list()

    def current_dictionary(self) -> str:
        return DictionariesManager.get_current_dict()

    def set_dictionary(self, language: str) -> None:
        DictionariesManager.set_lang(language)

    def set_permission(self, permission_id: str, enabled: bool) -> None:
        PermissionsManager.set_auto_grant(permission_id, enabled)
