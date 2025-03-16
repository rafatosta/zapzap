from PyQt6.QtCore import QTimer
from PyQt6.QtDBus import QDBusInterface
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from enum import Enum
from zapzap.resources.ThemeStylesheet import ThemeStylesheet
from zapzap.services.SettingsManager import SettingsManager


class ThemeManager:
    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    _instance = None

    # Dicionário com temas
    
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
            self.current_theme = ThemeManager.Type(
                SettingsManager.get("system/theme", ThemeManager.Type.Auto)
            )
            self.timer = QTimer()
            # Verifica o tema do sistema a cada segundo
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.sync_system_theme)

    # === Métodos Públicos ===
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
            instance.sync_system_theme()
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

    @staticmethod
    def sync():
        """Força a sincronização do tema atual."""
        instance = ThemeManager.instance()
        instance._apply_theme()

    # === Sincronização e Aplicação de Temas ===
    def sync_system_theme(self):
        """Sincroniza o tema do sistema com o tema atual."""
        theme = self._detect_system_theme()
        if self.current_theme != theme:
            self.current_theme = theme
            self._apply_theme()

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

    # === Implementação dos Temas Claro e Escuro ===
    def _apply_light_theme(self):
        """Aplica o tema claro."""
        print("Aplicando tema claro...")
        palette = self._create_palette(
            window="#f7f5f3", text="#000000", base="#f0f0f0", highlight="#0066cc"
        )
        self._apply_palette(palette)
        QApplication.instance().getWindow().browser.set_theme_light()
        QApplication.instance().setStyleSheet(ThemeStylesheet.get_stylesheet('light'))

    def _apply_dark_theme(self):
        """Aplica o tema escuro."""
        print("Aplicando tema escuro...")
        palette = self._create_palette(
            window="#1d1f1f", text="#ffffff", base="#3a3a3a", highlight="#0099ff"
        )
        self._apply_palette(palette)
        QApplication.instance().getWindow().browser.set_theme_dark()
        QApplication.instance().setStyleSheet(ThemeStylesheet.get_stylesheet('dark'))

    def _create_palette(self, window, text, base, highlight):
        """Cria uma paleta com cores fornecidas."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(window))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
        palette.setColor(QPalette.ColorRole.Base, QColor(base))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(base))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(text))
        palette.setColor(QPalette.ColorRole.Text, QColor(text))
        palette.setColor(QPalette.ColorRole.Button, QColor(base))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(text))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(text))
        return palette

    def _apply_palette(self, palette):
        """Aplica a paleta ao aplicativo."""
        QApplication.instance().setPalette(palette)

    # === Detecção do Tema do Sistema ===
    def _detect_system_theme(self) -> Type:
        """
        Determina o tema do sistema usando a interface D-Bus.
        Retorna:
            - ThemeManager.Type.Dark se o tema escuro for preferido
            - ThemeManager.Type.Light se o tema claro for preferido
        """
        try:
            interface = QDBusInterface(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Settings",
            )
            msg = interface.call(
                "Read", "org.freedesktop.appearance", "color-scheme")
            color_scheme = msg.arguments()[0]
            return ThemeManager.Type.Dark if color_scheme == 1 else ThemeManager.Type.Light
        except Exception as e:
            print(f"Erro ao obter o tema do sistema: {e}")
            return ThemeManager.Type.Light
