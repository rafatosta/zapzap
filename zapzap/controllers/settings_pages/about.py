from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from zapzap.view.about_page import Ui_About
from gettext import gettext as _
import zapzap
from zapzap.theme.builder_icon import getImageQPixmap


class About(QWidget, Ui_About):

    emitCloseSettings = pyqtSignal()

    def __init__(self):
        super(About, self).__init__()
        self.setupUi(self)

        self.version_app.setText(
            _(self.version_app.text()).format(id=zapzap.__version__))
        # actions

        def leanMore():
            QDesktopServices.openUrl(QUrl(zapzap.__website__))
            self.emitCloseSettings.emit()
        self.btnLeanMore.clicked.connect(leanMore)

        def reportIssue():
            QDesktopServices.openUrl(QUrl(zapzap.__bugreport__))
            self.emitCloseSettings.emit()
        self.btnReportIssue.clicked.connect(reportIssue)
