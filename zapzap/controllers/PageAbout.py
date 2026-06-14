from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl, PYQT_VERSION_STR, QT_VERSION_STR

from zapzap.resources.UserIcon import UserIcon
from zapzap.services.EnvironmentDetector import EnvironmentDetector
from zapzap.views.ui_page_about import Ui_PageAbout
from zapzap import __bugreport__, __website__, __version__, __appname__, __donationPage__

from gettext import gettext as _


class PageAbout(QWidget, Ui_PageAbout):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._setup_ui()
        self._configure_signals()

    def _setup_ui(self):
        self.icon.setIcon(UserIcon.get_icon())
        self.name_app.setText(__appname__)

        self.version_app.setText(
            _(self.version_app.text()).format(id=__version__))

        self.qt_version.setText(
            f'Qt:{QT_VERSION_STR} - PyQt:{PYQT_VERSION_STR}')

        self._setValueLabel(self.labelBuildChannel,
                            EnvironmentDetector.CHANNEL)

        self._setValueLabel(self.labelBuildProvider,
                            EnvironmentDetector.PROVIDER)

        self._setValueLabel(self.labelBuildRepository,
                            EnvironmentDetector.BUILD_REPOSITORY)

    def _setValueLabel(self, label, value):
        label.setText(
            _(label.text()).format(value=value)
        )

    def _configure_signals(self):
        self.btnLeanMore.clicked.connect(
            lambda:  QDesktopServices.openUrl(QUrl(__website__)))

        self.btnReportIssue.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__bugreport__)))

        self.btnDonate.clicked.connect(
            lambda:  QDesktopServices.openUrl(QUrl(__donationPage__)))
