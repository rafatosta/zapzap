"""Model for account card state and persistence."""

from __future__ import annotations

from zapzap.features.accounts.domain.user import User
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings_manager import SettingsManager


class CardUserModel:
    """Wraps a User with account-card persistence helpers."""

    def __init__(self, user: User):
        self.user = user

    @property
    def is_default_user(self) -> bool:
        return self.user.id == User.USER_DEFAULT

    @property
    def name(self) -> str:
        return self.user.name

    @name.setter
    def name(self, value: str) -> None:
        self.user.name = value

    @property
    def enabled(self) -> bool:
        return bool(self.user.enable)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.user.enable = bool(value)

    @property
    def notifications_enabled(self) -> bool:
        return bool(SettingsManager.get(f"{self.user.id}/notification", True))

    @notifications_enabled.setter
    def notifications_enabled(self, value: bool) -> None:
        SettingsManager.set(f"{self.user.id}/notification", bool(value))

    @property
    def user_agent(self) -> str:
        return SettingsManager.get(f"{self.user.id}/user_agent", "Default")

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        SettingsManager.set(f"{self.user.id}/user_agent", value)

    def regenerate_icon(self) -> None:
        self.user.icon = UserIcon.get_new_icon_svg()

    def restore_default_icon(self) -> None:
        self.user.icon = UserIcon.ICON_DEFAULT

    def remove_user(self) -> None:
        self.user.remove()

    def current_icon(self):
        user_icon_type = UserIcon.Type.Default
        if not self.enabled:
            user_icon_type = UserIcon.Type.Disable
        elif not self.notifications_enabled:
            user_icon_type = UserIcon.Type.Silence
        return UserIcon.get_icon(self.user.icon, user_icon_type)

    @staticmethod
    def available_user_agents():
        from zapzap.features.browser.web.web_view import WebView

        return list(WebView.USER_AGENTS.keys())
