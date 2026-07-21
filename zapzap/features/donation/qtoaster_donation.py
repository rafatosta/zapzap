"""Backward-compatible donation toaster import."""

from zapzap.features.donation.controller import DonationController


class QtoasterDonation(DonationController):
    """Compatibility alias for the MVC donation controller."""
