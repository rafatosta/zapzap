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
            _("Define which permissions can be granted automatically to WhatsApp Web."),
            parent,
        )
        self.setObjectName("PermissionsSettingsView")
        self.permission_rows = {}
        self.permission_sections = {}
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_permissions_section()
        self._setup_flatpak_section()

    def _setup_permissions_section(self):
        self.add_section(
            SettingsInfoBox(
                _(
                    "Disabled permissions will continue to be requested when needed."
                )
            )
        )

        actions = QWidget()
        actions.setObjectName("GlobalPermissionActions")
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 4)
        actions_layout.setSpacing(8)
        actions_layout.addStretch(1)
        self.btn_allow_all = Button(_("Allow all"))
        self.btn_remove_all = Button(_("Remove all"))
        actions_layout.addWidget(self.btn_allow_all)
        actions_layout.addWidget(self.btn_remove_all)
        self.add_section(actions)

        groups = (
            (
                "device_access",
                _("Device access"),
                (
                    (
                        "microphone",
                        _("Microphone"),
                        _("Automatically allow access to your microphone."),
                    ),
                    (
                        "camera",
                        _("Camera"),
                        _("Automatically allow access to your camera."),
                    ),
                    (
                        "camera_microphone",
                        _("Camera and microphone"),
                        _(
                            "Automatically allow simultaneous access to the "
                            "camera and microphone."
                        ),
                    ),
                    (
                        "location",
                        _("Location"),
                        _("Automatically allow access to your location."),
                    ),
                ),
            ),
            (
                "sharing",
                _("Sharing"),
                (
                    (
                        "screen_contents",
                        _("Screen sharing"),
                        _("Automatically allow sharing of screen contents."),
                    ),
                    (
                        "screen_contents_audio",
                        _("Screen with audio"),
                        _("Automatically allow screen sharing with audio."),
                    ),
                ),
            ),
            (
                "advanced",
                _("Advanced"),
                (
                    (
                        "mouse_lock",
                        _("Pointer lock"),
                        _("Automatically allow the page to capture the mouse pointer."),
                    ),
                ),
            ),
        )

        for group_id, title, rows in groups:
            section = SettingsSection(title)
            section.setObjectName(f"PermissionSection_{group_id}")
            card = SettingsCard()
            for permission_id, row_title, description in rows:
                row = SettingsSwitchRow(row_title, description)
                self.permission_rows[permission_id] = row
                card.add_row(row)
            section.add_card(card)
            self.permission_sections[group_id] = section
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
