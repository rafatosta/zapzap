"""Persistence facade for the initial setup flow."""

from __future__ import annotations

from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.features.permissions.permissions_manager import PermissionsManager
from zapzap.features.startup.autostart_manager import AutostartManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager


class InitialSetupModel:
    """Centralizes settings read/write operations used by onboarding.

    This model hides SettingsManager keys from the initial setup controller.
    Controllers should access setup values through semantic properties and
    methods instead of passing raw persistence keys around.
    """

    _COMPLETED = ("onboarding/initial_setup_completed", False)
    _THEME = ("system/theme", ThemeManager.Type.Auto.value)
    _NOTIFICATIONS_ENABLED = ("notification/app", True)
    _NOTIFICATION_SHOW_PHOTO = ("notification/show_photo", True)
    _NOTIFICATION_SHOW_NAME = ("notification/show_name", True)
    _NOTIFICATION_SHOW_MESSAGE_PREVIEW = ("notification/show_msg", True)
    _TRAY_ICON = ("system/tray_icon", True)
    _TRAY_NOTIFICATION_COUNTER = ("system/notificationCounter", False)
    _QUIT_IN_CLOSE = ("system/quit_in_close", False)
    _CONFIRM_ON_CLOSE = ("system/confirm_on_close", False)
    _START_SYSTEM = ("system/start_system", False)
    _START_BACKGROUND = ("system/start_background", False)
    _SPELLCHECKERS = ("system/spellCheckers", True)
    _WEBRTC_SHIELD = ("privacy/webrtc_shield", False)

    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    @classmethod
    def is_completed(cls) -> bool:
        return cls._get_bool(cls._COMPLETED)

    @classmethod
    def mark_completed(cls) -> None:
        cls._set_bool(cls._COMPLETED, True)

    @staticmethod
    def _get_bool(setting: tuple[str, bool]) -> bool:
        key, default = setting
        return bool(SettingsManager.get(key, default))

    @staticmethod
    def _set_bool(setting: tuple[str, bool], value: bool) -> None:
        key, _default = setting
        SettingsManager.set(key, bool(value))

    @staticmethod
    def _get_str(setting: tuple[str, str]) -> str:
        key, default = setting
        return str(SettingsManager.get(key, default))

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
        return self._get_str(self._THEME)

    def set_theme(self, theme: str) -> None:
        ThemeManager.set_theme(theme)

    @property
    def notifications_enabled(self) -> bool:
        return self._get_bool(self._NOTIFICATIONS_ENABLED)

    @notifications_enabled.setter
    def notifications_enabled(self, value: bool) -> None:
        self._set_bool(self._NOTIFICATIONS_ENABLED, value)

    @property
    def notification_show_photo(self) -> bool:
        return self._get_bool(self._NOTIFICATION_SHOW_PHOTO)

    @notification_show_photo.setter
    def notification_show_photo(self, value: bool) -> None:
        self._set_bool(self._NOTIFICATION_SHOW_PHOTO, value)

    @property
    def notification_show_name(self) -> bool:
        return self._get_bool(self._NOTIFICATION_SHOW_NAME)

    @notification_show_name.setter
    def notification_show_name(self, value: bool) -> None:
        self._set_bool(self._NOTIFICATION_SHOW_NAME, value)

    @property
    def notification_show_message_preview(self) -> bool:
        return self._get_bool(self._NOTIFICATION_SHOW_MESSAGE_PREVIEW)

    @notification_show_message_preview.setter
    def notification_show_message_preview(self, value: bool) -> None:
        self._set_bool(self._NOTIFICATION_SHOW_MESSAGE_PREVIEW, value)

    @property
    def tray_icon_enabled(self) -> bool:
        return self._get_bool(self._TRAY_ICON)

    @tray_icon_enabled.setter
    def tray_icon_enabled(self, value: bool) -> None:
        SysTrayManager.set_state(bool(value))

    @property
    def tray_notification_counter(self) -> bool:
        return self._get_bool(self._TRAY_NOTIFICATION_COUNTER)

    @tray_notification_counter.setter
    def tray_notification_counter(self, value: bool) -> None:
        self._set_bool(self._TRAY_NOTIFICATION_COUNTER, value)

    @property
    def keep_running_in_background(self) -> bool:
        return not self._get_bool(self._QUIT_IN_CLOSE)

    @keep_running_in_background.setter
    def keep_running_in_background(self, value: bool) -> None:
        self._set_bool(self._QUIT_IN_CLOSE, not value)

    @property
    def confirm_on_close(self) -> bool:
        return self._get_bool(self._CONFIRM_ON_CLOSE)

    @confirm_on_close.setter
    def confirm_on_close(self, value: bool) -> None:
        self._set_bool(self._CONFIRM_ON_CLOSE, value)

    def set_autostart(self, enabled: bool) -> None:
        self._set_bool(self._START_SYSTEM, enabled)
        AutostartManager.create_desktop_file(bool(enabled))

    @property
    def autostart_enabled(self) -> bool:
        return self._get_bool(self._START_SYSTEM)

    @autostart_enabled.setter
    def autostart_enabled(self, value: bool) -> None:
        self.set_autostart(value)

    @property
    def start_minimized(self) -> bool:
        return self._get_bool(self._START_BACKGROUND)

    @start_minimized.setter
    def start_minimized(self, value: bool) -> None:
        self._set_bool(self._START_BACKGROUND, value)

    @property
    def spellcheck_enabled(self) -> bool:
        return self._get_bool(self._SPELLCHECKERS)

    @spellcheck_enabled.setter
    def spellcheck_enabled(self, value: bool) -> None:
        self._set_bool(self._SPELLCHECKERS, value)

    @property
    def webrtc_shield_enabled(self) -> bool:
        return self._get_bool(self._WEBRTC_SHIELD)

    @webrtc_shield_enabled.setter
    def webrtc_shield_enabled(self, value: bool) -> None:
        self._set_bool(self._WEBRTC_SHIELD, value)

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
