from gettext import gettext as _

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_QtoasterDonation(object):
    def setupUi(self, QtoasterDonation):
        QtoasterDonation.setObjectName("QtoasterDonation")
        QtoasterDonation.resize(715, 169)
        QtoasterDonation.setWindowTitle("")
        QtoasterDonation.setStyleSheet("#frame{\n"
"border:1px solid #374151;\n"
"border-radius:12px;\n"
"background-color:#1d1f1f;\n"
"color:white;\n"
"}\n"
"QLabel{color:white;}\n"
"#labelZapZap{font:700 20pt;}\n"
"#labelWelcomeTo{font:10pt;}\n"
"#labelVersion{color:#d1d5db;font:10pt;}\n"
"#labelSubtitle{color:#d1d5db;font:8pt;}\n"
"#donateButton{\n"
"background:#22c55e;\n"
"border:none;\n"
"border-radius:10px;\n"
"color:white;\n"
"padding:10px;\n"
"font-weight:bold;\n"
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
"}")
        self.horizontalLayout = QtWidgets.QHBoxLayout(QtoasterDonation)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(parent=QtoasterDonation)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerFrame = QtWidgets.QFrame(parent=self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.headerFrame.sizePolicy().hasHeightForWidth())
        self.headerFrame.setSizePolicy(sizePolicy)
        self.headerFrame.setMinimumSize(QtCore.QSize(0, 16))
        self.headerFrame.setMaximumSize(QtCore.QSize(16777215, 16))
        self.headerFrame.setObjectName("headerFrame")
        self.footerLayout_2 = QtWidgets.QHBoxLayout(self.headerFrame)
        self.footerLayout_2.setContentsMargins(0, 0, 0, 0)
        self.footerLayout_2.setSpacing(0)
        self.footerLayout_2.setObjectName("footerLayout_2")
        self.labelVersion = QtWidgets.QLabel(parent=self.headerFrame)
        self.labelVersion.setText("")
        self.labelVersion.setObjectName("labelVersion")
        self.footerLayout_2.addWidget(self.labelVersion)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.footerLayout_2.addItem(spacerItem)
        self.closeButton = QtWidgets.QToolButton(parent=self.headerFrame)
        self.closeButton.setStyleSheet("\n"
"                QToolButton {\n"
"                padding: 5px;\n"
"                }\n"
"                QToolButton:hover {\n"
"                background-color: #1d1f1f;\n"
"                }\n"
"         ")
        self.closeButton.setText("")
        self.closeButton.setAutoRaise(True)
        self.closeButton.setObjectName("closeButton")
        self.footerLayout_2.addWidget(self.closeButton)
        self.verticalLayout.addWidget(self.headerFrame)
        self.infoFrame = QtWidgets.QHBoxLayout()
        self.infoFrame.setObjectName("infoFrame")
        self.logo = QtWidgets.QPushButton(parent=self.frame)
        self.logo.setMinimumSize(QtCore.QSize(82, 82))
        self.logo.setMaximumSize(QtCore.QSize(82, 82))
        self.logo.setStyleSheet("background-color: transparent;\n"
"border-color: transparent;")
        self.logo.setText("")
        self.logo.setIconSize(QtCore.QSize(82, 82))
        self.logo.setObjectName("logo")
        self.infoFrame.addWidget(self.logo)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labelWelcomeTo = QtWidgets.QLabel(parent=self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.labelWelcomeTo.setFont(font)
        self.labelWelcomeTo.setObjectName("labelWelcomeTo")
        self.verticalLayout_3.addWidget(self.labelWelcomeTo)
        self.labelZapZap = QtWidgets.QLabel(parent=self.frame)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        self.labelZapZap.setFont(font)
        self.labelZapZap.setObjectName("labelZapZap")
        self.verticalLayout_3.addWidget(self.labelZapZap)
        self.labelSubtitle = QtWidgets.QLabel(parent=self.frame)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        self.labelSubtitle.setFont(font)
        self.labelSubtitle.setScaledContents(True)
        self.labelSubtitle.setWordWrap(True)
        self.labelSubtitle.setObjectName("labelSubtitle")
        self.verticalLayout_3.addWidget(self.labelSubtitle)
        self.infoFrame.addLayout(self.verticalLayout_3)
        spacerItem1 = QtWidgets.QSpacerItem(98, 17, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.infoFrame.addItem(spacerItem1)
        self.donateButton = QtWidgets.QPushButton(parent=self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.donateButton.sizePolicy().hasHeightForWidth())
        self.donateButton.setSizePolicy(sizePolicy)
        self.donateButton.setMinimumSize(QtCore.QSize(220, 54))
        self.donateButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.donateButton.setObjectName("donateButton")
        self.infoFrame.addWidget(self.donateButton)
        self.verticalLayout.addLayout(self.infoFrame)
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
        spacerItem2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.footerLayout.addItem(spacerItem2)
        self.moreButton = QtWidgets.QToolButton(parent=self.footerFrame)
        font = QtGui.QFont()
        self.moreButton.setFont(font)
        self.moreButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.moreButton.setObjectName("moreButton")
        self.footerLayout.addWidget(self.moreButton)
        self.verticalLayout.addWidget(self.footerFrame)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(QtoasterDonation)
        QtCore.QMetaObject.connectSlotsByName(QtoasterDonation)

    def retranslateUi(self, QtoasterDonation):
        
        self.labelWelcomeTo.setText(_("Support the project"))
        self.labelZapZap.setText(_("ZapZap"))
        self.labelSubtitle.setText(_("Sua doação ajuda a manter o projeto no ar, melhorar recursos e garantir sua privacidade e liberdade."))
        self.donateButton.setText(_("❤ Make a donation"))
        self.donationMessage.setText(_("Não mostrar novamente"))
        self.moreButton.setText(_("Saiba mais sobre o ZapZap ↗"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    QtoasterDonation = QtWidgets.QWidget()
    ui = Ui_QtoasterDonation()
    ui.setupUi(QtoasterDonation)
    QtoasterDonation.show()
    sys.exit(app.exec())
