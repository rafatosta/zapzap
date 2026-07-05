from __future__ import annotations

from dataclasses import dataclass

from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SetupManager import SetupManager
from zapzap.services.ThemeManager import ThemeManager


@dataclass(frozen=True)
class InitialSetupState:
    """Read-only data needed to render the initial setup view."""

    values: dict
    packaging: str
    is_flatpak: bool


class InitialSetupModel:
    """Persistence and environment facade for the first-run setup flow."""

    VERSION = 3
    KEY_COMPLETED = "onboarding/completed"
    KEY_VERSION = "onboarding/version"
    KEY_LAST_ENVIRONMENT = "onboarding/last_environment"

    @staticmethod
    def current_environment() -> str:
        return "flatpak" if SetupManager._is_flatpak else "local"

    def should_show(self) -> bool:
        completed = SettingsManager.get(self.KEY_COMPLETED, False)
        version = int(SettingsManager.get(self.KEY_VERSION, 0))
        last_environment = SettingsManager.get(self.KEY_LAST_ENVIRONMENT, "")

        if not completed:
            return True
        if version != self.VERSION:
            return True
        return last_environment != self.current_environment()

    def get_state(self) -> InitialSetupState:
        return InitialSetupState(
            values=self.get_initial_values(),
            packaging=EnvironmentManager.identify_packaging().value,
            is_flatpak=SetupManager._is_flatpak,
        )

    def get_initial_values(self) -> dict:
        return {
            "theme": SettingsManager.get(
                "system/theme", ThemeManager.Type.Auto.value
            ),
            "scale": int(SettingsManager.get("system/scale", 100)),
            "sidebar": SettingsManager.get("system/sidebar", True),
            "menubar": SettingsManager.get("system/menubar", True),
            "tray_icon": SettingsManager.get("system/tray_icon", True),
            "notification_counter": SettingsManager.get(
                "system/notificationCounter", False
            ),
            "start_background": SettingsManager.get(
                "system/start_background", False
            ),
            "start_system": SettingsManager.get("system/start_system", False),
            "confirm_on_close": SettingsManager.get(
                "system/confirm_on_close", False
            ),
            "quit_in_close": SettingsManager.get("system/quit_in_close", False),
            "spellcheck": SettingsManager.get("system/spellCheckers", True),
            "use_qt_file_dialog": SettingsManager.get(
                "system/DontUseNativeDialog", False
            ),
            "wayland": SettingsManager.get("system/wayland", False),
            "notifications_enabled": SettingsManager.get("notification/app", True),
            "show_message_preview": SettingsManager.get(
                "notification/show_msg", True
            ),
            "show_name": SettingsManager.get("notification/show_name", True),
            "show_photo": SettingsManager.get("notification/show_photo", True),
            "donation_message": SettingsManager.get(
                "notification/donation_message", False
            ),
        }

    def save_preferences(self, values: dict):
        SettingsManager.set("system/start_background", values["start_background"])
        SettingsManager.set("system/quit_in_close", values["quit_in_close"])
        SettingsManager.set("system/start_system", values["start_system"])
        AutostartManager.create_desktop_file(values["start_system"])
        SettingsManager.set("system/confirm_on_close", values["confirm_on_close"])
        SettingsManager.set(
            "system/DontUseNativeDialog", values["use_qt_file_dialog"]
        )
        SettingsManager.set("system/sidebar", values["sidebar"])
        SettingsManager.set("system/menubar", values["menubar"])
        SettingsManager.set("system/tray_icon", values["tray_icon"])
        SettingsManager.set(
            "system/notificationCounter", values["notification_counter"]
        )
        SettingsManager.set("system/scale", values["scale"])
        SettingsManager.set("system/theme", values["theme"])
        SettingsManager.set("notification/app", values["notifications_enabled"])
        SettingsManager.set("notification/show_msg", values["show_message_preview"])
        SettingsManager.set("notification/show_name", values["show_name"])
        SettingsManager.set("notification/show_photo", values["show_photo"])
        SettingsManager.set(
            "notification/donation_message", values["donation_message"]
        )
        SettingsManager.set("system/spellCheckers", values["spellcheck"])
        SettingsManager.set("system/wayland", values["wayland"])

    def mark_as_completed(self):
        SettingsManager.set(self.KEY_COMPLETED, True)
        SettingsManager.set(self.KEY_VERSION, self.VERSION)
        SettingsManager.set(self.KEY_LAST_ENVIRONMENT, self.current_environment())
