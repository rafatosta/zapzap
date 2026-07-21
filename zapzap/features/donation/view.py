"""View for the donation reminder toaster."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QFont

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.ui.components import Button
from zapzap.ui.components import CheckBox
from zapzap.ui.components import CloseButton
from zapzap.ui.components import Label


class DonationView(QWidget):
    """Donation toaster layout and positioning without application behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.corner = QtCore.Qt.Corner.TopLeftCorner
        self.margin = 10

        self._setup_ui()
        self._setup_view()

    def _setup_ui(self) -> None:
        self.setObjectName("QtoasterDonation")
        self.resize(707, 172)
        self.setWindowTitle("")
        self.setStyleSheet(
            "QWidget#QtoasterDonation {"
            "background: transparent;"
            "}"
            "QFrame#frame {"
            "border: 1px solid palette(mid);"
            "border-radius: 12px;"
            "background-color: palette(base);"
            "color: palette(text);"
            "}"
            "QFrame#footerFrame {"
            "border-top: 1px solid palette(mid);"
            "}"
            "QToolButton#moreButton {"
            "border: 1px solid transparent;"
            "border-radius: 8px;"
            "padding: 6px 8px;"
            "background: transparent;"
            "color: palette(highlight);"
            "}"
            "QToolButton#moreButton:hover {"
            "background: palette(alternate-base);"
            "border-color: palette(mid);"
            "}"
        )

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.frame = QtWidgets.QFrame(parent=self)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout.addWidget(self.frame)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")

        self._setup_header()
        self._setup_content()
        self._setup_footer()
        self._retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

    def _setup_header(self) -> None:
        self.headerFrame = QtWidgets.QFrame(parent=self.frame)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.headerFrame.setSizePolicy(sizePolicy)

        # Espaço suficiente para o botão de 28px
        self.headerFrame.setFixedHeight(36)
        self.headerFrame.setObjectName("headerFrame")

        self.footerLayout_2 = QtWidgets.QHBoxLayout(self.headerFrame)

        # Pequeno respiro nas laterais e no topo
        self.footerLayout_2.setContentsMargins(2, 2, 2, 6)
        self.footerLayout_2.setSpacing(8)
        self.footerLayout_2.setObjectName("footerLayout_2")

        self.labelVersion = Label(
            variant="muted",
            parent=self.headerFrame,
        )
        self.labelVersion.setText("")
        self.labelVersion.setObjectName("labelVersion")

        self.footerLayout_2.addWidget(
            self.labelVersion,
            0,
            QtCore.Qt.AlignmentFlag.AlignVCenter,
        )

        self.footerLayout_2.addStretch()

        self.closeButton = CloseButton(parent=self.headerFrame)

        self.footerLayout_2.addWidget(
            self.closeButton,
            0,
            QtCore.Qt.AlignmentFlag.AlignTop
            | QtCore.Qt.AlignmentFlag.AlignRight,
        )

        self.verticalLayout.addWidget(self.headerFrame)

    def _setup_content(self) -> None:
        self.infoFrame = QtWidgets.QHBoxLayout()
        self.infoFrame.setObjectName("infoFrame")

        self.logo = QtWidgets.QPushButton(parent=self.frame)
        self.logo.setMinimumSize(QtCore.QSize(82, 82))
        self.logo.setMaximumSize(QtCore.QSize(82, 82))
        self.logo.setStyleSheet("background: transparent; border: none;")
        self.logo.setText("")
        self.logo.setIconSize(QtCore.QSize(82, 82))
        self.logo.setObjectName("logo")
        self.infoFrame.addWidget(self.logo)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.labelZapZap = Label(variant="title", parent=self.frame)
        self.labelZapZap.setObjectName("labelZapZap")
        self.verticalLayout_3.addWidget(self.labelZapZap)

        self.labelSubtitle = Label(variant="brand", parent=self.frame)
        self.labelSubtitle.setScaledContents(True)
        self.labelSubtitle.setObjectName("labelSubtitle")
        self.verticalLayout_3.addWidget(self.labelSubtitle)

        self.infoFrame.addLayout(self.verticalLayout_3)
        self.infoFrame.addItem(
            QtWidgets.QSpacerItem(
                98,
                17,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
        )

        self.donateButton = Button("", parent=self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHeightForWidth(
            self.donateButton.sizePolicy().hasHeightForWidth())
        self.donateButton.setSizePolicy(sizePolicy)
        self.donateButton.setMinimumSize(QtCore.QSize(220, 54))
        self.donateButton.setObjectName("donateButton")
        self.infoFrame.addWidget(self.donateButton)
        self.verticalLayout.addLayout(self.infoFrame)

    def _setup_footer(self) -> None:
        self.footerFrame = QtWidgets.QFrame(parent=self.frame)
        self.footerFrame.setObjectName("footerFrame")

        self.footerLayout = QtWidgets.QHBoxLayout(self.footerFrame)
        self.footerLayout.setContentsMargins(0, 9, 0, 0)
        self.footerLayout.setSpacing(0)
        self.footerLayout.setObjectName("footerLayout")

        self.donationMessage = CheckBox(parent=self.footerFrame)
        self.footerLayout.addWidget(self.donationMessage)
        self.footerLayout.addItem(
            QtWidgets.QSpacerItem(
                0,
                0,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
        )

        self.moreButton = QtWidgets.QToolButton(parent=self.footerFrame)
        self.moreButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        font = self.moreButton.font()
        font.setWeight(QFont.Weight.Medium)
        self.moreButton.setFont(font)

        self.moreButton.setObjectName("moreButton")
        self.footerLayout.addWidget(self.moreButton)
        self.verticalLayout.addWidget(self.footerFrame)

    def _retranslate_ui(self) -> None:
        self.labelZapZap.setText(_("ZapZap"))
        self.labelSubtitle.setText(
            _(
                "Your donation helps keep the project running, improve resources "
                "and guarantee your privacy and freedom."
            )
        )
        self.donateButton.setText(_("❤ Make a donation"))
        self.donationMessage.setText(_("Don't show again"))
        self.moreButton.setText(_("Learn more about ZapZap ↗"))

    def _setup_view(self) -> None:
        self.logo.setIcon(UserIcon.get_icon())
        self.setFocus()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        self._install_parent_resize_filter()
        self.raise_()
        self.adjustSize()

    def set_version_label(self, text: str) -> None:
        self.labelVersion.setText(text)

    def _install_parent_resize_filter(self) -> None:
        if self.parent() is not None:
            self.parent().installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            self.move_to_parent_corner()
        return super().eventFilter(source, event)

    def move_to_parent_corner(self) -> None:
        if self.parent() is None:
            return
        parent_rect = self.parent().rect()
        geometry = self.geometry()
        geometry.moveBottomLeft(
            parent_rect.bottomLeft() + QtCore.QPoint(self.margin + 45, -self.margin)
        )
        self.setGeometry(geometry)

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)
