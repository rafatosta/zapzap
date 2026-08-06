"""Controller for the donation reminder toaster."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from zapzap.features.alerts.external_url import open_external_url
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
        window = QApplication.instance().getWindow()
        window.open_donations()
        self.close()

    def _open_website(self) -> None:
        open_external_url(self.model.website_url, self)
