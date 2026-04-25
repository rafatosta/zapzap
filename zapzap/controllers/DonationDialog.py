from gettext import gettext as _
from urllib.parse import quote
from urllib.request import urlopen

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
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
    DIALOG_TITLE = "Apoie via Wise"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._qr_pixmap = QPixmap()

        self.setModal(True)
        self.setWindowTitle(_("Donation"))
        self.setMinimumWidth(520)

        self._build_ui()
        self._load_qr_code()

    def _build_ui(self):
        self.setStyleSheet(
            """
            QDialog { background: #FFFFFF; }
            QToolButton {
                background: #eef2e8;
                border-radius: 18px;
                min-width: 36px;
                min-height: 36px;
                font-size: 18px;
                color: #1F3D13;
            }
            QToolButton:hover { background: #dce7d4; }
            QLabel#dialog_title {
                font-size: 26px;
                font-weight: 900;
                color: #1F3D13;
            }
            QLabel#name_title {
                font-size: 34px;
                font-weight: 900;
            }
            QPushButton#primaryButton {
                background: #8ADD5D;
                border: 0;
                border-radius: 18px;
                padding: 12px 16px;
                font-size: 16px;
                font-weight: 700;
                color: #17350F;
            }
            QPushButton#primaryButton:hover { background: #96e86b; }
            QPushButton#secondaryButton {
                background: #E5ECD8;
                border: 0;
                border-radius: 18px;
                padding: 12px 16px;
                font-size: 16px;
                font-weight: 700;
                color: #17350F;
            }
            QPushButton#secondaryButton:hover { background: #dae6ca; }
            QPushButton#linkButton {
                background: #ECEFE9;
                border: 0;
                border-radius: 16px;
                padding: 10px 16px;
                font-size: 16px;
                font-weight: 700;
                color: #1F3D13;
                text-align: left;
            }
            QPushButton#linkButton:hover { background: #dce4d6; }
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        self.btn_close = QToolButton(self)
        self.btn_close.setText("✕")
        self.btn_close.setAutoRaise(True)
        self.btn_close.setToolTip(_("Close"))
        self.btn_close.clicked.connect(self.close)
        close_layout.addWidget(self.btn_close)
        root_layout.addLayout(close_layout)

        self.title_label = QLabel(self.DIALOG_TITLE, self)
        self.title_label.setObjectName("dialog_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(self.title_label)

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
        self.name_label.setObjectName("name_title")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(self.name_label)

        link_layout = QHBoxLayout()
        link_layout.setSpacing(8)
        self.link_button = QPushButton("wise.com/pay/me/rafaelt2487", self)
        self.link_button.setObjectName("linkButton")
        self.link_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.DONATION_LINK))
        )
        link_layout.addWidget(self.link_button)

        self.open_link_button = QToolButton(self)
        self.open_link_button.setText("↗")
        self.open_link_button.setToolTip(_("Open donation link"))
        self.open_link_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.DONATION_LINK))
        )
        link_layout.addWidget(self.open_link_button)
        root_layout.addLayout(link_layout)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        self.btn_copy = QPushButton(_("🔗 Copy link"), self)
        self.btn_copy.setObjectName("primaryButton")
        self.btn_copy.clicked.connect(self._copy_link)
        actions_layout.addWidget(self.btn_copy)

        self.btn_open = QPushButton(_("🌐 Open in browser"), self)
        self.btn_open.setObjectName("secondaryButton")
        self.btn_open.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.DONATION_LINK))
        )
        actions_layout.addWidget(self.btn_open)
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
