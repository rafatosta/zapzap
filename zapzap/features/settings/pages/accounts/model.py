"""Model for the Accounts settings page."""

from __future__ import annotations

from zapzap.models.User import User


class AccountsSettingsModel:
    """Model that exposes account persistence operations."""

    def list_users(self):
        """Return the users displayed by the accounts settings page."""
        return User.select()

    def create_user(self):
        """Create a new account, respecting the User model limits."""
        return User.create_new_user()
