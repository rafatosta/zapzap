"""View for explicit WebEngine permission settings."""

from gettext import gettext as _

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