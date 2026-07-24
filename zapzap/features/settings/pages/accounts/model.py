"""Model for the Accounts settings page."""

from __future__ import annotations

from zapzap import LIMITE_USERS
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.accounts.domain.user import User


class AccountsSettingsModel:
    """Model that exposes account persistence operations."""

    def list_users(self):
        """Return the users displayed by the accounts settings page."""
        return User.select()

    def create_user(self):
        """Create a new account, respecting the User model limits."""
        return User.create_new_user()

    def account_limit(self) -> int:
        """Return the configured account limit."""
        return int(SettingsManager.get("users/size", LIMITE_USERS))

    def account_count(self) -> int:
        """Return the number of persisted accounts."""
        return User.count_users()
