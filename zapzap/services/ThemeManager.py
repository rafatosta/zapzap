from PyQt6.QtCore import QTimer
from PyQt6.QtDBus import QDBusInterface
from PyQt6.QtWidgets import QApplication
from enum import Enum
from zapzap.services.SettingsManager import SettingsManager


class ThemeManager:
    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implementação do padrão Singleton."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa o ThemeManager com as configurações do sistema."""
        if not self._initialized:
            self._initialized = True
            # Obtém o tema salvo nas configurações do sistema (auto, claro ou escuro)
            self.current_theme = ThemeManager.Type(SettingsManager.get("system/theme", ThemeManager.Type.Auto))
            self.timer = QTimer()
            self.timer.setInterval(1000)  # Verifica o tema do sistema a cada segundo
            self.timer.timeout.connect(self.syncThemeSys)

    @staticmethod
    def instance() -> 'ThemeManager':
        """Obtém a instância singleton do ThemeManager."""
        if ThemeManager._instance is None:
            ThemeManager()
        return ThemeManager._instance

    @staticmethod
    def start():
        """Inicia o ThemeManager e sincroniza o tema com as configurações."""
        instance = ThemeManager.instance()
        if instance.current_theme == ThemeManager.Type.Auto:
            instance.timer.start()
            instance.syncThemeSys()  # Sincroniza com o tema do sistema
        else:
            instance._apply_theme()

    @staticmethod
    def set_theme(theme: Type):
        """Define o tema de acordo com a preferência do usuário."""
        instance = ThemeManager.instance()
        instance._set_user_theme(theme)

        # Salva o tema nas configurações
        SettingsManager.set("system/theme", theme.value)

    @staticmethod
    def get_current_theme() -> Type:
        """Obtém o tema atual."""
        return ThemeManager.instance().current_theme

    # === Sincronização com o Tema do Sistema ===
    def syncThemeSys(self):
        """Sincroniza o tema do sistema com o tema atual."""
        theme = self._get_system_theme()
        if self.current_theme != theme:
            self.current_theme = theme
            self._apply_theme()

    # === Funções de Configuração do Tema ===
    def _set_user_theme(self, theme: Type):
        """Define o tema com base na escolha do usuário."""
        if theme == ThemeManager.Type.Auto:
            self.timer.start()
        else:
            self.timer.stop()
            self.current_theme = theme
            self._apply_theme()

    def _apply_theme(self):
        """Aplica o tema atual."""
        if self.current_theme == ThemeManager.Type.Light:
            self._apply_light_theme()
        elif self.current_theme == ThemeManager.Type.Dark:
            self._apply_dark_theme()

    def _apply_light_theme(self):
        """Aplica o tema claro."""
        print("Aplicando tema claro...")
        self._set_theme_for_app()

    def _apply_dark_theme(self):
        """Aplica o tema escuro."""
        print("Aplicando tema escuro...")
        self._set_theme_for_app()

    # === Aplicação do Tema ===
    def _set_theme_for_app(self):
        """Aplica o tema para o aplicativo."""
        main_window = QApplication.instance().getWindow()
        main_window.set_theme_app()

    # === Detecção do Tema do Sistema ===
    def _get_system_theme(self) -> Type:
        """
        Determina o tema do sistema usando a interface D-Bus.
        Retorna:
            - ThemeManager.Type.Dark se o tema escuro for preferido
            - ThemeManager.Type.Light se o tema claro for preferido
        """
        try:
            name = "org.freedesktop.portal.Desktop"
            path = "/org/freedesktop/portal/desktop"
            interface = "org.freedesktop.portal.Settings"

            smp = QDBusInterface(name, path, interface)
            msg = smp.call("Read", "org.freedesktop.appearance", "color-scheme")
            color_scheme = msg.arguments()[0]

            return ThemeManager.Type.Dark if color_scheme == 1 else ThemeManager.Type.Light
        except Exception as e:
            print(f"Erro ao obter o tema do sistema: {e}")
            return ThemeManager.Type.Light
