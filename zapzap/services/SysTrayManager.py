from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon, QDesktopServices
from PyQt6.QtCore import QUrl

from gettext import gettext as _

from zapzap.resources.TrayIcon import TrayIcon
from zapzap import __donationPage__
from zapzap.services.SettingsManager import SettingsManager


class SysTrayManager:
    """Gerenciador para o ícone na bandeja do sistema."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implementação do padrão Singleton."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._initialize_components()

    @classmethod
    def instance(cls) -> 'SysTrayManager':
        """Obtém a instância Singleton do SysTrayManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_components(self):
        """Inicializa os componentes do gerenciador de bandeja."""
        self.number_notifications = 0
        self._tray = QSystemTrayIcon()
        self.current_icon = SettingsManager.get(
            "system/tray_theme", TrayIcon.Type.Default)
        self._set_icon(self.current_icon)

        self._actions = {
            "show": QAction(_("Show")),
            "settings": QAction(_("Settings")),
            "donation": QAction(_("Donation")),
            "exit": QAction(_("Quit")),
        }

        self._trayMenu = QMenu()
        self._trayMenu.addAction(self._actions["show"])
        self._trayMenu.addAction(self._actions["settings"])
        self._trayMenu.addAction(self._actions["donation"])
        self._trayMenu.addSeparator()
        self._trayMenu.addAction(self._actions["exit"])
        self._tray.setContextMenu(self._trayMenu)

        self._setup_connections()

    def _setup_connections(self):
        """Configura as conexões dos sinais das ações da bandeja."""
        main_window = QApplication.instance().getWindow()

        self._actions["show"].triggered.connect(main_window.show_window)
        self._actions["settings"].triggered.connect(main_window.open_settings)
        self._actions["donation"].triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__)))
        self._actions["exit"].triggered.connect(main_window.closeEvent)

    def _set_icon(self, icon_type: TrayIcon.Type, number_notifications=0):
        self._tray.setIcon(TrayIcon.getIcon(icon_type, number_notifications))

    # === Métodos Públicos ===

    @staticmethod
    def start():
        instance = SysTrayManager.instance()
        instance._load_state()

    @staticmethod
    def set_number_notifications(number_notifications):
        instance = SysTrayManager.instance()
        instance.number_notifications = number_notifications
        instance._set_icon(instance.current_icon, number_notifications)

    @staticmethod
    def set_theme(icon_type: TrayIcon.Type):
        instance = SysTrayManager.instance()
        instance._set_icon(icon_type, instance.number_notifications)
        SettingsManager.set(
            "system/tray_theme", icon_type)

    @staticmethod
    def _load_state():
        instance = SysTrayManager.instance()
        if SettingsManager.get("system/tray_icon", True):
            instance._tray.show()
        else:
            instance._tray.hide()

    def set_state(state: bool):
        instance = SysTrayManager.instance()
        if state:
            instance._tray.show()
        else:
            instance._tray.hide()

        SettingsManager.set("system/tray_icon", state)
