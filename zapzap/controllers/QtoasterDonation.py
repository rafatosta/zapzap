
from PyQt6.QtWidgets import QWidget
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from gettext import gettext as _
import zapzap
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.views.ui_qtoaster_donation import Ui_QtoasterDonation
from zapzap import __version__


class QtoasterDonation(QWidget, Ui_QtoasterDonation):
    def __init__(self, parent=None):
        super(QtoasterDonation, self).__init__()
        self.setupUi(self)
        self.setParent(parent)

        self.logo.setIcon(UserIcon.get_icon())

        self.labelVersion.setText(
            _(self.labelVersion.text()).format(id=__version__, version_type=_(EnvironmentManager.identify_packaging().value)))

        self.setFocus()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,
                           QtWidgets.QSizePolicy.Policy.Maximum)

        # we have a parent, install an eventFilter so that when it's resized
        # the notification will be correctly moved to the right corner
        self.parent().installEventFilter(self)

        # raise the widget and adjust its size to the minimum
        self.raise_()
        self.adjustSize()

        self.corner = QtCore.Qt.Corner.TopLeftCorner
        self.margin = 10

        # Configurações
        self.setUI()

    def setUI(self):
        # Close Button
        closeIcon = self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.closeButton.setIcon(closeIcon)
        self.closeButton.clicked.connect(self.close)

        # Donate Button
        def openDonation():
            self.close()
            QDesktopServices.openUrl(QUrl(zapzap.__donationPage__))
        self.donateButton.clicked.connect(openDonation)

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            parentRect = self.parent().rect()
            geo = self.geometry()
            geo.moveBottomLeft(
                parentRect.bottomLeft() + QtCore.QPoint(self.margin+45, -self.margin))
            self.setGeometry(geo)
        return super(QtoasterDonation, self).eventFilter(source, event)

    @staticmethod
    def showMessage(parent):
        qtoaster = QtoasterDonation(parent)
        qtoaster.show()

    def focusOutEvent(self, e):
        self.close()
