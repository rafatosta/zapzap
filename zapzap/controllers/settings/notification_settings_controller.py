from PyQt6.QtWidgets import QVBoxLayout, QWidget

from zapzap.views.pages.settings.notifications_settings_view import NotificationsSettingsView


class NotificationSettingsController(QWidget):
    """Classe responsável por gerenciar a página de notificações nas configurações."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._initialize()

    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = NotificationsSettingsView(self)
        layout.addWidget(self.view)
    
    def _initialize(self):
        """Inicializa a página carregando as configurações e configurando os sinais."""
        #self._load_settings()
        #self._connect_signals()
