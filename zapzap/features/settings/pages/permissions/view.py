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
            _("Permissões"),
            _("Defina quais permissões o WhatsApp Web pode receber automaticamente."),
            parent,
        )
        self.setObjectName("PermissionsSettingsView")
        self.permission_rows = {}
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        section = SettingsSection(
            _("Permissões"),
            _("Quando uma opção estiver desmarcada, o ZapZap perguntará novamente a cada sessão."),
        )
        card = SettingsCard()
        card.add_row(SettingsInfoBox(_(
            "Marque apenas as permissões que você deseja conceder automaticamente quando a página solicitar."
        )))

        rows = (
            ("microphone", _("Microfone"), _("Permitir automaticamente o acesso ao seu microfone.")),
            ("camera", _("Câmera"), _("Permitir automaticamente o acesso à sua câmera.")),
            (
                "camera_microphone",
                _("Câmera e microfone"),
                _("Permitir automaticamente o acesso simultâneo à câmera e ao microfone."),
            ),
            ("location", _("Localização"), _("Permitir automaticamente o acesso à sua localização.")),
            (
                "screen_contents",
                _("Conteúdo da tela"),
                _("Permitir automaticamente o compartilhamento do conteúdo da tela."),
            ),
            (
                "screen_contents_audio",
                _("Conteúdo da tela e áudio"),
                _("Permitir automaticamente o compartilhamento da tela com áudio."),
            ),
            ("mouse_lock", _("Bloqueio do mouse"), _("Permitir automaticamente que a página capture o ponteiro do mouse.")),
        )

        for permission_id, title, description in rows:
            row = SettingsSwitchRow(title, description)
            self.permission_rows[permission_id] = row
            card.add_row(row)

        section.add_card(card)
        self.add_section(section)
