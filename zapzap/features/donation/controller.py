"""Controller for the donation reminder toaster."""

from __future__ import annotations

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap.features.donation.model import DonationModel
from zapzap.features.donation.view import DonationView


class DonationController(DonationView):
    """Coordinates donation reminder presentation and user actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = DonationModel()
        self._load_model()
        self._connect_signals()

    @classmethod
    def should_show(cls) -> bool:
        return DonationModel.should_show_reminder()

    @staticmethod
    def showMessage(parent):
        donation = DonationController(parent)
        donation.show()
        return donation

    def _load_model(self) -> None:
        self.set_version_label(self.model.version_label)

    def _connect_signals(self) -> None:
        self.closeButton.clicked.connect(self.close)
        self.donationMessage.clicked.connect(self.model.disable_reminder)
        self.donateButton.clicked.connect(self._open_donation_page)
        self.moreButton.clicked.connect(self._open_website)

    def _open_donation_page(self) -> None:
        QDesktopServices.openUrl(QUrl(self.model.donation_url))

    def _open_website(self) -> None:
        QDesktopServices.openUrl(QUrl(self.model.website_url))
