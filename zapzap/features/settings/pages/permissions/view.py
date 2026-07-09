"""View for explicit WebEngine permission settings."""

from gettext import gettext as _

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from zapzap.ui.components import Button, LineEdit

from zapzap.features.settings.components import SettingsActionRow
from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsInfoBox
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsSection
from zapzap.features.settings.components import SettingsSwitchRow


class PermissionsSettingsView(SettingsPage):
    """Composable permissions settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Permissions"),
            _("Define which permissions WhatsApp Web can receive automatically."),
            parent,
        )
        self.setObjectName("PermissionsSettingsView")
        self.permission_rows = {}
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_permissions_section()
        self._setup_flatpak_section()

    def _setup_permissions_section(self):
        section = SettingsSection(
            _("Permissions"),
            _("When an option is unchecked, ZapZap will ask again in each session."),
        )
        card = SettingsCard()
        card.add_row(SettingsInfoBox(_(
            "Enable only the permissions you want to grant automatically when the page requests them."
        )))

        rows = (
            ("microphone", _("Microphone"), _("Automatically allow access to your microphone.")),
            ("camera", _("Camera"), _("Automatically allow access to your camera.")),
            (
                "camera_microphone",
                _("Camera and microphone"),
                _("Automatically allow simultaneous access to the camera and microphone."),
            ),
            ("location", _("Location"), _("Automatically allow access to your location.")),
            (
                "screen_contents",
                _("Screen contents"),
                _("Automatically allow sharing of screen contents."),
            ),
            (
                "screen_contents_audio",
                _("Screen contents and audio"),
                _("Automatically allow screen sharing with audio."),
            ),
            (
                "mouse_lock",
                _("Mouse lock"),
                _("Automatically allow the page to capture the mouse pointer."),
            ),
        )

        for permission_id, title, description in rows:
            row = SettingsSwitchRow(title, description)
            self.permission_rows[permission_id] = row
            card.add_row(row)

        section.add_card(card)
        self.add_section(section)

    def _setup_flatpak_section(self):
        self.flatpak_permissions_groupBox = SettingsSection(
            _("Flatpak permissions"),
            _("Grant filesystem access if downloads, imports, or dictionaries cannot reach folders outside the sandbox."),
        )
        card = SettingsCard()
        card.add_row(SettingsInfoBox(_(
            "Flatpak sandbox: if file access fails, grant folder permissions using Flatseal or flatpak override."
        ), "warning"))
        command_row = QWidget()
        command_layout = QHBoxLayout(command_row)
        command_layout.setContentsMargins(0, 8, 0, 8)
        self.flatpak_command_input = LineEdit()
        self.flatpak_command_input.setReadOnly(True)
        self.flatpak_command_input.setToolTip(
            _("Select and copy this command in your terminal")
        )
        self.btn_copy_flatpak_command = Button(_("Copy"))
        command_layout.addWidget(self.flatpak_command_input, 1)
        command_layout.addWidget(self.btn_copy_flatpak_command)
        self.btn_open_flatseal = SettingsActionRow(
            _("Flatseal"),
            _("Flatseal is a graphical utility to review and modify permissions from your Flatpak applications."),
            _("Install Flatseal on Linux | Flathub"),
        )
        card.add_row(command_row)
        card.add_row(self.btn_open_flatseal)
        self.btn_open_flatseal = self.btn_open_flatseal.button
        self.flatpak_permissions_groupBox.add_card(card)
        self.add_section(self.flatpak_permissions_groupBox)

    def configure_flatpak(self, is_flatpak):
        self.flatpak_permissions_groupBox.setVisible(is_flatpak)
