"""View for the Privacidade e rede settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class NetworkPrivacySettingsView(BaseSettingsContextView):
    """Composable view for Privacidade e rede settings."""

    def __init__(self, parent=None):
        sections = [('Rede', 'Defina proxy global ou por conta.', [('As configurações de proxy e privacidade serão migradas para este contexto MVC.', 'accent')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Privacidade e rede'), _('Configure proxy, WebRTC e opções de privacidade.'), translated_sections, parent)
