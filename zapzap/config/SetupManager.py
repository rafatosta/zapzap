from os import environ
from PyQt6.QtCore import QFileInfo
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.SettingsManager import SettingsManager


class SetupManager:
    """Gerencia as configurações de ambiente para o aplicativo."""

    _is_flatpak = QFileInfo(__file__).absolutePath().startswith('/app/')
    _qt_platform = "xcb"  # Valor padrão

    @staticmethod
    def apply():
        """
        Aplica configurações específicas de ambiente dependendo do ambiente de execução.
        Configura a plataforma gráfica e escalonamento de tela.
        """
        if not SetupManager._is_flatpak:
            SetupManager._qt_platform = "wayland" if SettingsManager.get(
                "system/wayland", False) else "xcb"
            environ['QT_QPA_PLATFORM'] = SetupManager._qt_platform

        environ['QT_SCALE_FACTOR'] = str(int(SettingsManager.get(
            "system/scale", 100))/100)
        environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

        environ["QTWEBENGINE_DICTIONARIES_PATH"] = DictionariesManager.get_path()

        environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"

    @staticmethod
    def get_argv():
        """
        Gera uma lista de argumentos para configurar o comportamento do QWebEngine.

        Cada argumento é controlado por uma chave no SettingsManager, permitindo que 
        seja habilitado ou desabilitado conforme necessário. Se a chave não existir 
        no SettingsManager, será usado o valor padrão especificado.

        Opções disponíveis:
        1. --in-process-gpu: Usa o mesmo processo para GPU e renderização.
        Chave: "performance/in_process_gpu" (bool, padrão: False)
        2. --disable-gpu: Desabilita o uso da GPU.
        Chave: "performance/disable_gpu" (bool, padrão: False)
        3. --single-process: Executa tudo em um único processo (pode causar instabilidade).
        Chave: "performance/single_process" (bool, padrão: False)
        """
        arguments = []

        if SettingsManager.get("performance/in_process_gpu", False):
            arguments.append("--in-process-gpu")
        if SettingsManager.get("performance/disable_gpu", False):
            arguments.append("--disable-gpu")
        if SettingsManager.get("performance/single_process", False):
            arguments.append("--single-process")

        print("Configurações para QWebEngine:\n\t", arguments)

        return arguments
