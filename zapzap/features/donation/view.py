"""View for the donation reminder toaster."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

from zapzap.assets.icons.user_icon import UserIcon
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
            "#frame{\n"
            "border:1px solid #374151;\n"
            "border-radius:12px;\n"
            "background-color:#1d1f1f;\n"
            "color:white;\n"
            "}\n"
            "QLabel{color:white;}\n"
            "#labelZapZap{font-size:20pt;}\n"
            "#labelWelcomeTo{font:10pt;}\n"
            "#labelVersion{color:#d1d5db;font:10pt;}\n"
            "#labelSubtitle{color:#d1d5db;font:8pt;}\n"
            "#donateButton{\n"
            "background:#22c55e;\n"
            "border:none;\n"
            "border-radius:10px;\n"
            "color:white;\n"
            "padding:10px;\n"
            "}\n"
            "#footerFrame{\n"
            "border-top:1px solid #374151;\n"
            "}\n"
            "#donationMessage{\n"
            "    color: rgb(192, 191, 188);\n"
            "}\n"
            "#moreButton{\n"
            "border:none;\n"
            "color:rgb(46, 194, 126);\n"
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
        sizePolicy.setHeightForWidth(self.headerFrame.sizePolicy().hasHeightForWidth())
        self.headerFrame.setSizePolicy(sizePolicy)
        self.headerFrame.setMinimumSize(QtCore.QSize(0, 22))
        self.headerFrame.setMaximumSize(QtCore.QSize(16777215, 16))
        self.headerFrame.setObjectName("headerFrame")

        self.footerLayout_2 = QtWidgets.QHBoxLayout(self.headerFrame)
        self.footerLayout_2.setContentsMargins(0, 0, 0, 0)
        self.footerLayout_2.setSpacing(0)
        self.footerLayout_2.setObjectName("footerLayout_2")

        self.labelVersion = Label(parent=self.headerFrame)
        self.labelVersion.setText("")
        self.labelVersion.setObjectName("labelVersion")
        self.footerLayout_2.addWidget(self.labelVersion)
        self.footerLayout_2.addItem(
            QtWidgets.QSpacerItem(
                0,
                0,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
        )

        self.closeButton = QtWidgets.QToolButton(parent=self.headerFrame)
        self.closeButton.setStyleSheet(
            "\n"
            "                QToolButton {\n"
            "                padding: 5px;\n"
            "                }\n"
            "                QToolButton:hover {\n"
            "                background-color: #1d1f1f;\n"
            "                }\n"
            "         "
        )
        self.closeButton.setText("")
        self.closeButton.setAutoRaise(True)
        self.closeButton.setObjectName("closeButton")
        self.footerLayout_2.addWidget(self.closeButton)
        self.verticalLayout.addWidget(self.headerFrame)

    def _setup_content(self) -> None:
        self.infoFrame = QtWidgets.QHBoxLayout()
        self.infoFrame.setObjectName("infoFrame")

        self.logo = QtWidgets.QPushButton(parent=self.frame)
        self.logo.setMinimumSize(QtCore.QSize(82, 82))
        self.logo.setMaximumSize(QtCore.QSize(82, 82))
        self.logo.setStyleSheet("background-color: transparent;\nborder-color: transparent;")
        self.logo.setText("")
        self.logo.setIconSize(QtCore.QSize(82, 82))
        self.logo.setObjectName("logo")
        self.infoFrame.addWidget(self.logo)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.labelZapZap = Label(parent=self.frame)
        title_font = QtGui.QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QtGui.QFont.Weight.DemiBold)
        title_font.setItalic(False)
        self.labelZapZap.setFont(title_font)
        self.labelZapZap.setObjectName("labelZapZap")
        self.verticalLayout_3.addWidget(self.labelZapZap)

        self.labelSubtitle = Label(parent=self.frame)
        subtitle_font = QtGui.QFont()
        subtitle_font.setPointSize(8)
        subtitle_font.setWeight(QtGui.QFont.Weight.Normal)
        subtitle_font.setItalic(False)
        self.labelSubtitle.setFont(subtitle_font)
        self.labelSubtitle.setScaledContents(True)
        self.labelSubtitle.setWordWrap(True)
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

        self.donateButton = QtWidgets.QPushButton(parent=self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHeightForWidth(self.donateButton.sizePolicy().hasHeightForWidth())
        self.donateButton.setSizePolicy(sizePolicy)
        self.donateButton.setMinimumSize(QtCore.QSize(220, 54))
        self.donateButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        button_font = self.donateButton.font()
        button_font.setWeight(QtGui.QFont.Weight.Medium)
        self.donateButton.setFont(button_font)
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

        self.donationMessage = QtWidgets.QCheckBox(parent=self.footerFrame)
        self.donationMessage.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.donationMessage.setObjectName("donationMessage")
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
        self.moreButton.setFont(QtGui.QFont())
        self.moreButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
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
        self.set_close_icon()
        self._install_parent_resize_filter()
        self.raise_()
        self.adjustSize()

    def set_close_icon(self) -> None:
        close_icon = self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton,
        )
        self.closeButton.setIcon(close_icon)

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
