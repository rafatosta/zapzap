from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSize, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon
from zapzap.view.donations_page import Ui_Donations
import zapzap


class Donations(QWidget, Ui_Donations):
    def __init__(self):
        super(Donations, self).__init__()
        self.setupUi(self)
        self.loadDonations()

    def loadDonations(self):
        self.btn_paypal.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/PayPal.png'))
        self.btn_paypal.setIconSize(QSize(150, 80))
        self.btn_paypal.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__paypal__)))

        self.btn_pix.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/pix.png'))
        self.btn_pix.setIconSize(QSize(150, 80))
        self.btn_pix.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__pix__)))

        self.btn_kofi.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/kofi.svg'))
        self.btn_kofi.setIconSize(QSize(150, 80))
        self.btn_kofi.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__kofi__)))

        self.btn_gitSponor.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/sponsor.svg'))
        self.btn_gitSponor.setIconSize(QSize(150, 80))
        self.btn_gitSponor.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__githubSponor__)))
