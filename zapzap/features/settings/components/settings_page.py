from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from zapzap.ui.components import Label
from zapzap.features.settings.components.settings_restart_bar import SettingsRestartBar


class SettingsPage(QScrollArea):
    """
    Página base rolável para telas de configurações.

    Fornece uma estrutura padrão com título, descrição opcional e um layout
    vertical onde seções e componentes de configuração podem ser adicionados.
    """

    def __init__(self, title, description="", parent=None):
        """
        Inicializa a página de configurações.

        Args:
            title:
                Título principal exibido no topo da página.

            description:
                Texto opcional exibido abaixo do título para contextualizar
                a página.

            parent:
                Widget pai da página.
        """
        super().__init__(parent)

        self.setObjectName("SettingsPageScroll")
        self.setWidgetResizable(True)

        self.viewport_widget = QWidget()
        self.viewport_widget.setObjectName("SettingsPageViewport")
        self.setWidget(self.viewport_widget)

        self.content_layout = QVBoxLayout(self.viewport_widget)
        self.content_layout.setContentsMargins(32, 28, 32, 32)
        self.content_layout.setSpacing(9)

        self.title_label = Label(title, "title")
        self.title_label.setObjectName("SettingsPageTitle")
        self.content_layout.addWidget(self.title_label)

        self.description_label = None

        if description:
            self.description_label = Label(description, "description")
            self.description_label.setObjectName("SettingsPageDescription")
            self.description_label.setWordWrap(True)
            self.content_layout.addWidget(self.description_label)

        self.content_layout.addSpacing(18)

        self.restart_bar = SettingsRestartBar(self.viewport())
        self._apply_style()

    def add_section(self, section):
        """
        Adiciona uma seção ou componente ao conteúdo da página.

        Args:
            section:
                Widget que será inserido no layout vertical da página.
        """
        self.content_layout.addWidget(section)

    def add_stretch(self):
        """
        Adiciona um espaçamento flexível ao final da página.

        Útil para empurrar o conteúdo para o topo quando houver pouco conteúdo
        disponível na área visível.
        """
        self.content_layout.addStretch(1)

    def set_restart_required(self, restart_kind=None):
        """Show or hide the contextual restart action."""
        self.restart_bar.set_restart_kind(restart_kind)
        if restart_kind:
            self._position_restart_bar()

    def _position_restart_bar(self):
        margin = 16
        width = max(320, self.viewport().width() - (margin * 2))
        height = self.restart_bar.sizeHint().height()
        self.restart_bar.setGeometry(
            margin,
            self.viewport().height() - height - margin,
            width,
            height,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_restart_bar()

    def _apply_style(self):
        """
        Aplica o estilo visual base da página.

        Define fundo transparente para a área de rolagem e utiliza as cores
        da paleta atual do sistema para o viewport interno.
        """
        self.setStyleSheet("""
            QScrollArea#SettingsPageScroll {
                border: 0;
                background: transparent;
            }

            QScrollArea#SettingsPageScroll > QWidget > QWidget,
            QWidget#SettingsPageViewport {
                background: palette(window);
                color: palette(text);
            }
        """)
