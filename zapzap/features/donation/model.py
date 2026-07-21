"""Model for donation reminder state and metadata."""

from __future__ import annotations

from gettext import gettext as _

from zapzap import __donationPage__, __version__, __website__
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.environment_detector import EnvironmentDetector


class DonationModel:
    """Centralizes donation reminder data and persistence access."""

    _DONATION_MESSAGE_KEY = "notification/donation_message"
    _DONATION_MESSAGE_DEFAULT = True

    @classmethod
    def should_show_reminder(cls) -> bool:
        """Return whether the donation reminder should be shown."""
        return not SettingsManager.get(
            cls._DONATION_MESSAGE_KEY,
            cls._DONATION_MESSAGE_DEFAULT,
        )

    @property
    def version_label(self) -> str:
        """Formatted application version and runtime distribution label."""
        packaging = _(EnvironmentDetector.PACKAGING)
        channel = _(EnvironmentDetector.CHANNEL)
        return f"v{__version__} - {packaging} - {channel}"

    @property
    def donation_url(self) -> str:
        return __donationPage__

    @property
    def website_url(self) -> str:
        return __website__

    def disable_reminder(self) -> None:
        """Persist that donation reminders should not be shown again."""
        SettingsManager.set(self._DONATION_MESSAGE_KEY, True)
