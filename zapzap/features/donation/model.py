"""Model for donation reminder state and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from gettext import gettext as _
from typing import Tuple

from zapzap import (
    __donationPage__,
    __githubSponsor__,
    __kofi__,
    __paypal__,
    __pix__,
    __version__,
    __website__,
    __wise__,
)
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.environment_detector import EnvironmentDetector


@dataclass(frozen=True)
class DonationMethod:
    """One official external contribution destination."""

    identifier: str
    title: str
    description: str
    url: str
    icon_name: str


def donation_methods() -> Tuple[DonationMethod, ...]:
    """Build translated presentation metadata around centralized URLs."""

    return (
        DonationMethod(
            "github_sponsors",
            _("GitHub Sponsors"),
            _(
                "Support ZapZap through GitHub and help fund its long-term "
                "development."
            ),
            __githubSponsor__,
            "donation_code",
        ),
        DonationMethod(
            "pix",
            _("Pix"),
            _(
                "Continue securely in your browser and complete the "
                "contribution with your banking app."
            ),
            __pix__,
            "donation_pix",
        ),
        DonationMethod(
            "paypal",
            _("PayPal"),
            _("A simple and secure way to support ZapZap from anywhere."),
            __paypal__,
            "donation_card",
        ),
        DonationMethod(
            "wise",
            _("Wise"),
            _(
                "International contributions with reduced fees and "
                "competitive exchange rates."
            ),
            __wise__,
            "donation_transfer",
        ),
        DonationMethod(
            "kofi",
            _("Ko-fi"),
            _(
                "Make a one-time or recurring contribution and help keep "
                "the project active."
            ),
            __kofi__,
            "donation_cup",
        ),
    )


class DonationModel:
    """Centralizes donation reminder data and persistence access."""

    _DONATION_MESSAGE_KEY = "notification/donation_message"
    # The legacy setting stores whether the reminder is hidden.
    _DONATION_MESSAGE_HIDDEN_DEFAULT = False

    @classmethod
    def should_show_reminder(cls) -> bool:
        """Return whether the donation reminder should be shown."""
        return not SettingsManager.get(
            cls._DONATION_MESSAGE_KEY,
            cls._DONATION_MESSAGE_HIDDEN_DEFAULT,
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
