from gettext import gettext as _
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap.resources.TrayIcon import TrayIcon
from zapzap import __donationPage__
from zapzap.services.SettingsManager import SettingsManager


class SysTrayManager:
    """Gerenciador do ícone na bandeja do sistema (System Tray)."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implementação do padrão Singleton."""
        if cls._instance is None:
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
        self.current_icon = TrayIcon.Type(
            SettingsManager.get("system/tray_theme", TrayIcon.Type.Default)
        )
        self._set_icon(self.current_icon)

        self._actions = self._create_actions()
        self._trayMenu = self._create_menu()
        self._tray.setContextMenu(self._trayMenu)

        self._setup_connections()

    def _create_actions(self):
        """Cria as ações disponíveis no menu da bandeja."""
        return {
            "show": QAction(_("Show")),
            "settings": QAction(_("Settings")),
            "donation": QAction(_("Donation")),
            "exit": QAction(_("Quit")),
        }

    def _create_menu(self):
        """Cria o menu da bandeja do sistema."""
        tray_menu = QMenu()
        tray_menu.addAction(self._actions["show"])
        tray_menu.addAction(self._actions["settings"])
        tray_menu.addAction(self._actions["donation"])
        tray_menu.addSeparator()
        tray_menu.addAction(self._actions["exit"])
        return tray_menu

    def _setup_connections(self):
        """Configura as conexões dos sinais das ações da bandeja."""
        main_window = QApplication.instance().getWindow()

        self._tray.activated.connect(main_window.show_window)

        self._actions["show"].triggered.connect(main_window.show_window)
        self._actions["settings"].triggered.connect(
            lambda: self._open_settings(main_window))
        self._actions["donation"].triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__))
        )
        self._actions["exit"].triggered.connect(main_window.closeEvent)

    def _set_icon(self, icon_type: TrayIcon.Type, number_notifications=0):
        """Atualiza o ícone da bandeja."""
        self.current_icon = icon_type

        print("notificationCounter: ", SettingsManager.get(
            "system/notificationCounter", False))

        if SettingsManager.get(
                "system/notificationCounter", False):
            number_notifications = 0

        self._tray.setIcon(TrayIcon.getIcon(icon_type, number_notifications))

    def _open_settings(self, main_window):
        main_window.open_settings()
        main_window.showNormal()
        main_window.activateWindow()
        main_window.raise_()

    @staticmethod
    def start():
        """Inicia o SysTrayManager e carrega o estado inicial."""
        instance = SysTrayManager.instance()
        instance._load_state()

    @staticmethod
    def set_number_notifications(number_notifications):
        """Define o número de notificações exibidas no ícone."""
        instance = SysTrayManager.instance()
        instance.number_notifications = number_notifications
        instance._set_icon(instance.current_icon, number_notifications)

    @staticmethod
    def set_theme(icon_type: TrayIcon.Type):
        """Define o tema do ícone na bandeja."""
        instance = SysTrayManager.instance()
        instance._set_icon(icon_type, instance.number_notifications)
        SettingsManager.set("system/tray_theme", icon_type.value)

    @staticmethod
    def refresh():
        instance = SysTrayManager.instance()
        instance._set_icon(instance.current_icon,
                           instance.number_notifications)

    @staticmethod
    def _load_state():
        """Carrega o estado da visibilidade do ícone na bandeja."""
        instance = SysTrayManager.instance()
        if SettingsManager.get("system/tray_icon", True):
            instance._tray.show()
        else:
            instance._tray.hide()

    @staticmethod
    def set_state(state: bool = True):
        """Define a visibilidade do ícone na bandeja."""
        instance = SysTrayManager.instance()
        if state:
            instance._tray.show()
        else:
            instance._tray.hide()
        SettingsManager.set("system/tray_icon", state)
