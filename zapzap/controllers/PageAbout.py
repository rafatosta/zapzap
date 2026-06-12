from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl, PYQT_VERSION_STR, QT_VERSION_STR

from zapzap.resources.UserIcon import UserIcon
from zapzap.services.EnvironmentDetector import EnvironmentDetector
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.views.ui_page_about import Ui_PageAbout
from zapzap import __bugreport__, __website__, __version__, __appname__

from gettext import gettext as _


class PageAbout(QWidget, Ui_PageAbout):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._setup_ui()

        # self.icon.setIcon(UserIcon.get_icon())

        # v_type = _("Official compilation") if EnvironmentManager.isOfficial() else _(
        #    """Unofficial""")

        # v_package = EnvironmentManager.identify_packaging().value if EnvironmentManager.isOfficial() else _(
        #    """Unknown""")

        # self.version_app.setText(
        #    _(self.version_app.text()).format(id=__version__, version_type=v_type, package=v_package))

        # self.btnLeanMore.clicked.connect(
        #    lambda:  QDesktopServices.openUrl(QUrl(__website__)))

        # self.btnReportIssue.clicked.connect(
        #    lambda: QDesktopServices.openUrl(QUrl(__bugreport__)))

    def _setup_ui(self):
        self.icon.setIcon(UserIcon.get_icon())
        self.name_app.setText(__appname__)

        self.version_app.setText(
            _(self.version_app.text()).format(id=__version__, package="Flatpak | AppImage | None"))

        self.qt_version.setText(
            f'Qt:{QT_VERSION_STR} - PyQt:{PYQT_VERSION_STR}')

        self._setValueLabel(self.labelBuildChannel,
                            EnvironmentDetector.CHANNEL)

        self._setValueLabel(self.labelBuildProvider,
                            EnvironmentDetector.PROVIDER)

        self._setValueLabel(self.labelBuildCommit,
                            EnvironmentDetector.COMMIT[:7])

    def _setValueLabel(self, label, value):
        label.setText(
            _(label.text()).format(value=value)
        )
