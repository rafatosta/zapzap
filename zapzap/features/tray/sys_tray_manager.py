from gettext import gettext as _
import sys
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QCursor

from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.config.settings.system import SystemSettings


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
        self._settings = AppearanceSettings()
        self.number_notifications = 0
        self._tray = QSystemTrayIcon()
        self.current_icon = TrayIcon.Type(self._settings.tray_theme)
        self._set_icon(self.current_icon)

        self._actions = self._create_actions()
        self._trayMenu = self._create_menu()

        # Linux StatusNotifier/AppIndicator hosts may consume primary/context
        # clicks without emitting QSystemTrayIcon.activated unless a native
        # context menu is attached. Keep that native integration on Linux;
        # Windows/macOS use the explicit activation routing below.
        self._native_context_menu = sys.platform.startswith("linux")
        if self._native_context_menu:
            self._tray.setContextMenu(self._trayMenu)

        self._activation_timer = QTimer(self._tray)
        self._activation_timer.setSingleShot(True)
        self._activation_timer.timeout.connect(self._toggle_bound_window)

        self._setup_connections()

    def _create_actions(self):
        """Cria as ações disponíveis no menu da bandeja."""
        return {
            "show": QAction(_("Show")),
            "mute": QAction(
                _("Unmute") if SystemSettings().audio_muted else _("Mute")
            ),
            "settings": QAction(_("Settings")),
            "donation": QAction(_("Support ZapZap")),
            "exit": QAction(_("Quit")),
        }

    def _create_menu(self):
        """Cria o menu da bandeja do sistema."""
        tray_menu = QMenu()
        tray_menu.addAction(self._actions["show"])
        tray_menu.addAction(self._actions["mute"])
        tray_menu.addAction(self._actions["settings"])
        tray_menu.addAction(self._actions["donation"])
        tray_menu.addSeparator()
        tray_menu.addAction(self._actions["exit"])
        return tray_menu

    def _setup_connections(self):
        """Configura as conexões dos sinais das ações da bandeja."""
        main_window = QApplication.instance().getWindow()

        if main_window is None:
            for widget in QApplication.topLevelWidgets():
                if widget.inherits("MainWindow"):
                    main_window = widget
                    break

        if main_window:
            self.bind_window(main_window)

    def _toggle_bound_window(self):
        main_window = getattr(self, "_bound_window", None)
        if main_window is not None:
            main_window.show_window()

    def _show_tray_menu(self):
        if self._trayMenu.isVisible():
            return
        self._trayMenu.popup(QCursor.pos())

    def _schedule_primary_toggle(self):
        application = QApplication.instance()
        interval = (
            application.doubleClickInterval()
            if application is not None
            else 400
        )
        self._activation_timer.start(max(1, int(interval)))

    def _on_tray_activated(self, reason):
        activation = QSystemTrayIcon.ActivationReason

        if self._native_context_menu:
            # StatusNotifier/AppIndicator hosts own the context menu on Linux.
            # Do not popup a second QMenu from the application: doing so can
            # leave the shell cursor busy while it resolves two menu requests.
            if reason in {
                activation.Trigger,
                activation.DoubleClick,
            }:
                # GNOME AppIndicator commonly exposes its "activate" gesture
                # as Trigger even when that gesture came from a double click.
                if self._trayMenu.isVisible():
                    self._trayMenu.close()
                self._toggle_bound_window()
            return

        if reason == activation.Context:
            self._activation_timer.stop()
            self._show_tray_menu()
            return

        if reason == activation.DoubleClick:
            # Cancel the delayed first click so a double click toggles once.
            self._activation_timer.stop()
            self._toggle_bound_window()
            return

        if reason == activation.Trigger:
            # Delay a normal primary click just enough to distinguish it from
            # a double click on Windows/macOS and non-SNI tray backends.
            self._schedule_primary_toggle()
            return

        # Unknown and middle-click activations intentionally do nothing.

    @classmethod
    def bind_window(cls, main_window):
        """Reconnect tray actions to the current MainWindow instance."""
        instance = cls.instance()
        instance._activation_timer.stop()
        instance._disconnect_window_actions()
        instance._bound_window = main_window
        instance._tray.activated.connect(instance._on_tray_activated)
        instance._actions["show"].triggered.connect(main_window.show_window)
        instance._actions["mute"].triggered.connect(
            main_window.toggle_audio_muted
        )
        instance._actions["settings"].triggered.connect(
            lambda: instance._open_settings(main_window))
        instance._actions["donation"].triggered.connect(
            lambda: instance._open_donations(main_window))
        instance._actions["exit"].triggered.connect(main_window.request_quit)

    def _disconnect_window_actions(self):
        for signal in (
            self._tray.activated,
            self._actions["show"].triggered,
            self._actions["mute"].triggered,
            self._actions["settings"].triggered,
            self._actions["donation"].triggered,
            self._actions["exit"].triggered,
        ):
            try:
                signal.disconnect()
            except TypeError:
                pass

    def _set_icon(self, icon_type: TrayIcon.Type, number_notifications=0):
        """Atualiza o ícone da bandeja."""
        self.current_icon = icon_type

        if not self._settings.notification_counter_enabled:
            number_notifications = 0

        self._tray.setIcon(TrayIcon.getIcon(icon_type, number_notifications))

        # Qt forwards this to the native taskbar/dock on supported platforms.
        # Older PyQt6 releases do not expose the badge API.
        set_badge = getattr(QApplication.instance(), "setBadgeNumber", None)
        if set_badge is not None:
            set_badge(number_notifications)

    def _open_settings(self, main_window):
        main_window.open_settings()
        main_window.restore_window()
        main_window.activateWindow()
        main_window.raise_()

    def _open_donations(self, main_window):
        main_window.open_donations()
        main_window.restore_window()
        main_window.activateWindow()
        main_window.raise_()

    @staticmethod
    def start():
        """Inicia o SysTrayManager e carrega o estado inicial."""
        instance = SysTrayManager.instance()
        instance._load_state()

    @classmethod
    def sync_audio_muted(cls, muted: bool) -> None:
        """Refresh the tray label without forcing tray initialization."""
        instance = cls._instance
        if instance is None or not hasattr(instance, "_actions"):
            return
        instance._actions["mute"].setText(
            _("Unmute") if muted else _("Mute")
        )

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
        instance._settings.tray_theme = icon_type.value

    @staticmethod
    def refresh():
        instance = SysTrayManager.instance()
        instance._set_icon(instance.current_icon,
                           instance.number_notifications)

    @staticmethod
    def _load_state():
        """Carrega o estado da visibilidade do ícone na bandeja."""
        instance = SysTrayManager.instance()
        if instance._settings.tray_icon_enabled:
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
        instance._settings.tray_icon_enabled = state
