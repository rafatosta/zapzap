from gettext import gettext as _

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from zapzap import __appname__, __bugreport__, __donationPage__, __version__, __website__
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.EnvironmentDetector import EnvironmentDetector
from zapzap.views.settings_components import SettingsActionRow, SettingsCard, SettingsInfoBox, SettingsPage, SettingsSection


class PageAbout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._configure_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(_("About"), _("Application identity, project links, support, legal information, and acknowledgements."), self)
        layout.addWidget(self.page)

        identity = SettingsSection(_("Application identity"))
        identity_card = SettingsCard()
        self.icon = QPushButton()
        self.icon.setIcon(UserIcon.get_icon())
        self.icon.setEnabled(False)
        self.name_app = QLabel(__appname__)
        self.version_app = QLabel(_("Version: {id}").format(id=__version__))
        self.qt_version = QLabel(f'Qt:{QT_VERSION_STR} - PyQt:{PYQT_VERSION_STR}')
        for widget in (self.icon, self.name_app, self.version_app, self.qt_version):
            identity_card.add_row(widget)
        identity.add_card(identity_card)
        self.page.add_section(identity)

        build = SettingsSection(_("Build information"))
        build_card = SettingsCard()
        self.labelBuildChannel = QLabel(_("Channel: {value}").format(value=_(EnvironmentDetector.CHANNEL)))
        self.labelBuildProvider = QLabel(_("Provider: {value}").format(value=_(EnvironmentDetector.PROVIDER)))
        self.labelBuildPackaging = QLabel(_("Packaging: {value}").format(value=_(EnvironmentDetector.PACKAGING)))
        self.labelBuildRepository = QLabel(_("Repository: {value}").format(value=_(EnvironmentDetector.BUILD_REPOSITORY)))
        for widget in (self.labelBuildChannel, self.labelBuildProvider, self.labelBuildPackaging, self.labelBuildRepository):
            build_card.add_row(widget)
        build.add_card(build_card)
        self.page.add_section(build)

        links = SettingsSection(_("Project links"))
        links_card = SettingsCard()
        self.btnLeanMore = SettingsActionRow(_("Homepage"), __website__, _("Open"))
        self.btnReportIssue = SettingsActionRow(_("Issue tracker"), __bugreport__, _("Report issue"))
        links_card.add_row(self.btnLeanMore)
        links_card.add_row(self.btnReportIssue)
        self.btnLeanMore = self.btnLeanMore.button
        self.btnReportIssue = self.btnReportIssue.button
        links.add_card(links_card)
        self.page.add_section(links)

        support = SettingsSection(_("Support"))
        support_card = SettingsCard()
        self.btnDonate = SettingsActionRow(_("Donate"), __donationPage__, _("Donate"))
        support_card.add_row(self.btnDonate)
        self.btnDonate = self.btnDonate.button
        support.add_card(support_card)
        self.page.add_section(support)

        legal = SettingsSection(_("Legal"))
        legal_card = SettingsCard()
        legal_card.add_row(SettingsInfoBox(_("ZapZap is licensed under GPL-3.0-or-later. ZapZap provides access to WhatsApp Web and is independent from WhatsApp and Meta.")))
        legal.add_card(legal_card)
        self.page.add_section(legal)
        self.page.add_stretch()

    def _setValueLabel(self, label, value):
        label.setText(_(label.text()).format(value=value))

    def _configure_signals(self):
        self.btnLeanMore.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(__website__)))
        self.btnReportIssue.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(__bugreport__)))
        self.btnDonate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(__donationPage__)))
