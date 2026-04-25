from gettext import gettext as _
from urllib.parse import quote
from urllib.request import urlopen

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class DonationDialog(QDialog):
    """Dialog com QR Code e informações para doação."""

    DONATION_LINK = "https://wise.com/pay/me/rafaelt2487"
    DONATION_LABEL = "@rafaelt2487"
    DONATION_NAME = "RAFAEL TOSTA SANTOS"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._qr_pixmap = QPixmap()

        self.setModal(True)
        self.setWindowTitle(_("Donation"))
        self.setMinimumWidth(520)

        self._build_ui()
        self._load_qr_code()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        self.btn_close = QToolButton(self)
        self.btn_close.setText("✕")
        self.btn_close.setAutoRaise(True)
        self.btn_close.setToolTip(_("Close"))
        self.btn_close.clicked.connect(self.close)
        close_layout.addWidget(self.btn_close)
        root_layout.addLayout(close_layout)

        qr_card = QFrame(self)
        qr_card.setStyleSheet("QFrame { background: #ECEFE9; border-radius: 22px; }")
        qr_layout = QVBoxLayout(qr_card)
        qr_layout.setContentsMargins(24, 24, 24, 24)
        qr_layout.setSpacing(14)

        self.qr_label = QLabel(_("Loading QR code..."), qr_card)
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)
        qr_layout.addWidget(self.qr_label)

        self.user_label = QLabel(self.DONATION_LABEL, qr_card)
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_label.setStyleSheet(
            "QLabel { background: #FFFFFF; border-radius: 16px; color: #1F3D13; font-weight: 700; padding: 8px 14px; }"
        )
        qr_layout.addWidget(self.user_label)

        root_layout.addWidget(qr_card, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.name_label = QLabel(self.DONATION_NAME, self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("QLabel { font-size: 34px; font-weight: 900; }")
        root_layout.addWidget(self.name_label)

        link_layout = QHBoxLayout()
        link_layout.setSpacing(8)
        self.link_button = QPushButton("wise.com/pay/me/rafaelt2487", self)
        self.link_button.setStyleSheet(
            "QPushButton { background: #ECEFE9; border-radius: 16px; padding: 8px 16px; font-weight: 600; }"
        )
        self.link_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.DONATION_LINK))
        )
        link_layout.addWidget(self.link_button)

        self.copy_small_button = QPushButton(_("Copy"), self)
        self.copy_small_button.setToolTip(_("Copy donation link"))
        self.copy_small_button.clicked.connect(self._copy_link)
        link_layout.addWidget(self.copy_small_button)
        root_layout.addLayout(link_layout)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        self.btn_copy = QPushButton(_("Copy link"), self)
        self.btn_copy.clicked.connect(self._copy_link)
        actions_layout.addWidget(self.btn_copy)

        self.btn_download = QPushButton(_("Download"), self)
        self.btn_download.clicked.connect(self._download_qr)
        actions_layout.addWidget(self.btn_download)
        root_layout.addLayout(actions_layout)

    def _load_qr_code(self):
        qr_endpoint = f"https://api.qrserver.com/v1/create-qr-code/?size=640x640&data={quote(self.DONATION_LINK)}"
        try:
            with urlopen(qr_endpoint, timeout=10) as response:
                self._qr_pixmap.loadFromData(response.read())
        except Exception:
            self._qr_pixmap = QPixmap()

        if self._qr_pixmap.isNull():
            self.qr_label.setText(_("Unable to load QR code. Use the link below to donate."))
            return

        scaled = self._qr_pixmap.scaled(
            300,
            300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.qr_label.setPixmap(scaled)

    def _copy_link(self):
        QApplication.clipboard().setText(self.DONATION_LINK)
        QMessageBox.information(self, _("Donation"), _("Donation link copied to clipboard."))

    def _download_qr(self):
        if self._qr_pixmap.isNull():
            QMessageBox.warning(self, _("Donation"), _("QR code is not available to download."))
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            _("Save QR code"),
            "zapzap-donation-qr.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg)",
        )
        if filename:
            self._qr_pixmap.save(filename)
