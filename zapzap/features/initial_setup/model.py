"""Persistence facade for the initial setup flow."""

from __future__ import annotations

from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.config.settings.notifications import NotificationSettings
from zapzap.core.config.settings.privacy import PrivacySettings
from zapzap.core.config.settings.spellcheck import SpellcheckSettings
from zapzap.core.config.settings.system import SystemSettings
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.features.permissions.permissions_manager import PermissionsManager
from zapzap.features.startup.autostart_manager import AutostartManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager


class InitialSetupModel(BaseSettings):
    """Centralizes settings read/write operations used by onboarding.

    This model hides SettingsManager keys from the initial setup controller.
    Controllers should access setup values through semantic properties and
    methods instead of passing raw persistence keys around.
    """

    _COMPLETED = ("onboarding/initial_setup_completed", False)

    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    def __init__(self) -> None:
        self._appearance_settings = AppearanceSettings()
        self._notification_settings = NotificationSettings()
        self._privacy_settings = PrivacySettings()
        self._spellcheck_settings = SpellcheckSettings()
        self._system_settings = SystemSettings()

    @classmethod
    def is_completed(cls) -> bool:
        return cls._get_bool(cls._COMPLETED)

    @classmethod
    def mark_completed(cls) -> None:
        cls._set_bool(cls._COMPLETED, True)

    def is_flatpak(self) -> bool:
        return SetupManager._is_flatpak

    def available_languages(self) -> list[str]:
        return TranslationManager.list_available_languages()

    def current_language(self) -> str:
        return TranslationManager.get_current_language()

    def set_language(self, language: str) -> None:
        TranslationManager.set_current_language(language)
        TranslationManager.apply()

    def current_theme(self) -> str:
        return self._appearance_settings.theme

    def set_theme(self, theme: str) -> None:
        ThemeManager.set_theme(theme)

    @property
    def notifications_enabled(self) -> bool:
        return self._notification_settings.enabled

    @notifications_enabled.setter
    def notifications_enabled(self, value: bool) -> None:
        self._notification_settings.enabled = value

    @property
    def notification_show_photo(self) -> bool:
        return self._notification_settings.show_photo

    @notification_show_photo.setter
    def notification_show_photo(self, value: bool) -> None:
        self._notification_settings.show_photo = value

    @property
    def notification_show_name(self) -> bool:
        return self._notification_settings.show_name

    @notification_show_name.setter
    def notification_show_name(self, value: bool) -> None:
        self._notification_settings.show_name = value

    @property
    def notification_show_message_preview(self) -> bool:
        return self._notification_settings.show_message_preview

    @notification_show_message_preview.setter
    def notification_show_message_preview(self, value: bool) -> None:
        self._notification_settings.show_message_preview = value

    @property
    def tray_icon_enabled(self) -> bool:
        return self._appearance_settings.tray_icon_enabled

    @tray_icon_enabled.setter
    def tray_icon_enabled(self, value: bool) -> None:
        SysTrayManager.set_state(bool(value))

    @property
    def tray_notification_counter(self) -> bool:
        return self._appearance_settings.notification_counter_enabled

    @tray_notification_counter.setter
    def tray_notification_counter(self, value: bool) -> None:
        self._appearance_settings.notification_counter_enabled = value

    @property
    def keep_running_in_background(self) -> bool:
        return self._system_settings.keep_running_in_background

    @keep_running_in_background.setter
    def keep_running_in_background(self, value: bool) -> None:
        self._system_settings.keep_running_in_background = value

    @property
    def confirm_on_close(self) -> bool:
        return self._system_settings.confirm_on_close

    @confirm_on_close.setter
    def confirm_on_close(self, value: bool) -> None:
        self._system_settings.confirm_on_close = value

    def set_autostart(self, enabled: bool) -> None:
        self._system_settings.start_with_system = enabled
        AutostartManager.create_desktop_file(bool(enabled))

    @property
    def autostart_enabled(self) -> bool:
        return self._system_settings.start_with_system

    @autostart_enabled.setter
    def autostart_enabled(self, value: bool) -> None:
        self.set_autostart(value)

    @property
    def start_minimized(self) -> bool:
        return self._system_settings.start_in_background

    @start_minimized.setter
    def start_minimized(self, value: bool) -> None:
        self._system_settings.start_in_background = value

    @property
    def spellcheck_enabled(self) -> bool:
        return self._spellcheck_settings.enabled

    @spellcheck_enabled.setter
    def spellcheck_enabled(self, value: bool) -> None:
        self._spellcheck_settings.enabled = value

    @property
    def webrtc_shield_enabled(self) -> bool:
        return self._privacy_settings.webrtc_shield_enabled

    @webrtc_shield_enabled.setter
    def webrtc_shield_enabled(self, value: bool) -> None:
        self._privacy_settings.webrtc_shield_enabled = value

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

    def microphone_permission_enabled(self) -> bool:
        return PermissionsManager.get_auto_grant("microphone")

    def set_microphone_permission(self, enabled: bool) -> None:
        self.set_permission("microphone", enabled)

    def camera_permission_enabled(self) -> bool:
        return PermissionsManager.get_auto_grant("camera")

    def set_camera_permission(self, enabled: bool) -> None:
        self.set_permission("camera", enabled)

    def screen_contents_permission_enabled(self) -> bool:
        return PermissionsManager.get_auto_grant("screen_contents")

    def set_screen_contents_permission(self, enabled: bool) -> None:
        self.set_permission("screen_contents", enabled)
