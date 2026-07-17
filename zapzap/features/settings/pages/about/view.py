"""View for the About settings page."""

from gettext import gettext as _
from PyQt6.QtCore import QSize

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.ui.components import Button, Label
from zapzap.features.settings.components import (
    SettingsActionRow,
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsSection,
)


class AboutSettingsView(SettingsPage):
    """Composable About page view without metadata or navigation logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("About"),
            _(
                "Application identity, project links, support, legal information, "
                "and acknowledgements."
            ),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_identity_section()
        self._setup_build_section()
        self._setup_links_section()
        self._setup_support_section()
        self._setup_legal_section()

    def _setup_identity_section(self):
        identity = SettingsSection(_("Application identity"))
        identity_card = SettingsCard()

        self.icon = Button()
        self.icon.setIcon(UserIcon.get_icon())
        self.icon.setMaximumSize(QSize(32, 32))
        self.icon.setStyleSheet("background-color: transparent;\n"
"border-color: transparent;")
        self.icon.setText("")
        self.icon.setIconSize(QSize(32, 32))
        self.icon.setFlat(True)

        self.name_app = Label("", "body")
        self.version_app = Label("", "body")
        self.qt_version = Label("", "muted")

        for widget in (
            self.icon,
            self.name_app,
            self.version_app,
            self.qt_version,
        ):
            identity_card.add_row(widget)

        identity.add_card(identity_card)
        self.add_section(identity)

    def _setup_build_section(self):
        build = SettingsSection(_("Build information"))
        build_card = SettingsCard()

        self.labelBuildChannel = Label("", "body")
        self.labelBuildProvider = Label("", "body")
        self.labelBuildPackaging = Label("", "body")
        self.labelBuildRepository = Label("", "body")

        for widget in (
            self.labelBuildChannel,
            self.labelBuildProvider,
            self.labelBuildPackaging,
            self.labelBuildRepository,
        ):
            build_card.add_row(widget)

        build.add_card(build_card)
        self.add_section(build)

    def _setup_links_section(self):
        links = SettingsSection(_("Project links"))
        links_card = SettingsCard()

        self.homepage_row = SettingsActionRow(_("Homepage"), " ", _("Open"))
        self.issue_row = SettingsActionRow(_("Issue tracker"), " ", _("Report issue"))
        self.btnLeanMore = self.homepage_row.button
        self.btnReportIssue = self.issue_row.button

        links_card.add_row(self.homepage_row)
        links_card.add_row(self.issue_row)
        links.add_card(links_card)
        self.add_section(links)

    def _setup_support_section(self):
        support = SettingsSection(_("Support"))
        support_card = SettingsCard()

        self.donate_row = SettingsActionRow(_("Donate"), " ", _("Donate"))
        self.btnDonate = self.donate_row.button

        support_card.add_row(self.donate_row)
        support.add_card(support_card)
        self.add_section(support)

    def _setup_legal_section(self):
        legal = SettingsSection(_("Legal"))
        legal_card = SettingsCard()
        legal_card.add_row(
            SettingsInfoBox(
                _(
                    "ZapZap is licensed under GPL-3.0-or-later. ZapZap provides "
                    "access to WhatsApp Web and is independent from WhatsApp and Meta."
                )
            )
        )
        legal.add_card(legal_card)
        self.add_section(legal)

    def set_identity(self, app_name: str, version: str, qt_version: str):
        self.name_app.setText(app_name)
        self.version_app.setText(_("Version: {id}").format(id=version))
        self.qt_version.setText(qt_version)

    def set_build_information(self, build_information):
        self.labelBuildChannel.setText(
            _("Channel: {value}").format(value=_(build_information["channel"]))
        )
        self.labelBuildProvider.setText(
            _("Provider: {value}").format(value=_(build_information["provider"]))
        )
        self.labelBuildPackaging.setText(
            _("Packaging: {value}").format(value=_(build_information["packaging"]))
        )
        self.labelBuildRepository.setText(
            _("Repository: {value}").format(value=_(build_information["repository"]))
        )

    def set_project_links(self, links):
        self.homepage_row.description_label.setText(links["website"])
        self.issue_row.description_label.setText(links["bug_report"])
        self.donate_row.description_label.setText(links["donation"])
