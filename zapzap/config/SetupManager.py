from os import environ
from PyQt6.QtCore import QFileInfo
from zapzap.services.SettingsManager import SettingsManager


class SetupManager:
    """Gerencia as configurações de ambiente para o aplicativo."""

    _abs_path = QFileInfo(__file__).absolutePath()
    _is_flatpak = _abs_path.startswith('/app/')

    @staticmethod
    def apply():
        """
        Aplica configurações específicas de ambiente dependendo do ambiente de execução.
        Configura a plataforma gráfica e escalonamento de tela.
        """
        if not SetupManager._is_flatpak:
            # Configuração da plataforma gráfica (Wayland ou XCB)
            environ['QT_QPA_PLATFORM'] = 'wayland' if SettingsManager.get("system/wayland", True) else 'xcb'

            # Configurações de escalonamento de tela
            environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
            environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'RoundPreferFloor'
