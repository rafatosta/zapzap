import logging
from os import environ, getenv
from PyQt6.QtCore import QFileInfo
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.SettingsManager import SettingsManager

# Configuração básica de logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


class SetupManager:
    """Gerencia as configurações de ambiente para o aplicativo."""

    _is_flatpak = QFileInfo(__file__).absolutePath().startswith('/app/')
    _qt_platform_xcb = "xcb"  # Valor padrão: X11

    @staticmethod
    def apply():
        """
        Aplica configurações específicas de ambiente dependendo do ambiente de execução.
        Configura a plataforma gráfica e escalonamento de tela.
        """
        # Configuração da plataforma gráfica
        if not SetupManager._is_flatpak:
            # Define a plataforma antes do Qt iniciar
            platform = SetupManager.get_qt_platform()
            if platform:
                environ["QT_QPA_PLATFORM"] = platform
                logger.info(
                    f"""Plataforma gráfica configurada: {environ['QT_QPA_PLATFORM']}""")
            else:
                 logger.info(
                    f"""Plataforma gráfica mantida : {environ.get('QT_QPA_PLATFORM')}""")

        else:
            logger.info(
                """Ambiente Flatpak detectado, plataforma gráfica não alterada.""")

        # Configuração de escalonamento de tela
        scale_factor = int(SettingsManager.get("system/scale", 100)) / 100
        environ["QT_SCALE_FACTOR"] = f'{scale_factor:.2f}'
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        logger.info(
            f"""Escalonamento de tela configurado: {scale_factor:.2f}""")

        # Configuração do caminho dos dicionários
        dictionary_path = DictionariesManager.get_path()
        environ["QTWEBENGINE_DICTIONARIES_PATH"] = dictionary_path
        logger.info(f"""QTWEBENGINE_DICTIONARIES_PATH configurado: {
            dictionary_path}""")

        # Permite a reprodução de áudios e arquivos mp4 ()
        # Recupera flags existentes (do sistema ou definidos pelo usuário via --setSettings)
        existing_flags = environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        settings_flags = SettingsManager.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        
        # Combina flags, priorizando ambiente > settings > hardcoded
        # Nota: Se o usuário define flags via env var, assumimos que ele sabe o que faz.
        # Se define via settings, concatenamos.
        
        # Vamos garantir que --disable-features=FFmpegAllowLists esteja presente
        required_flag = "--disable-features=FFmpegAllowLists"
        
        flags_list = []
        if existing_flags:
            flags_list.extend(existing_flags.split())
        if settings_flags:
            # Avoid duplicating flags if possible, though Chromium handles duplicates usually.
            # Convert to list to simple Append
            flags_list.extend(settings_flags.split())
             
        # Filter out potential conflicting flags
        # Remove --ozone-platform flags as they conflict with QT_QPA_PLATFORM
        final_flags = [f for f in flags_list if not f.startswith("--ozone-platform")]

        if required_flag not in final_flags:
             final_flags.append(required_flag)

        environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(final_flags)
        logger.info(f"QTWEBENGINE_CHROMIUM_FLAGS final: {environ['QTWEBENGINE_CHROMIUM_FLAGS']}")

        # Informação sobre o ambiente de execução
        SetupManager.printEnviron()

    @staticmethod
    def printEnviron():
        print(10*"-", "Environ", 10*"-")
        for k, v in environ.items():
            print(f"\t{k}: {v}")
        print(30*"-")

    @staticmethod
    def apply_qt_scale_factor_rounding_policy():
        """Deve ser aplicado após a criação da instância do app"""
        environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
        logger.info(
            "QT_SCALE_FACTOR_ROUNDING_POLICY configurado para RoundPreferFloor")

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

        logger.info(f"""Configurações para QWebEngine: {arguments}""")
        return arguments

    @staticmethod
    def get_qt_platform():
        # Se QT_QPA_PLATFORM já estiver definido no ambiente, respeita ele.
        if "QT_QPA_PLATFORM" in environ:
            return None

        # Verifica flag explicito --wayland
        import sys
        if "--wayland" in sys.argv:
            return "wayland"

        # Session Type
        XDG_SESSION_TYPE = getenv('XDG_SESSION_TYPE')
        print('XDG_SESSION_TYPE:', XDG_SESSION_TYPE)

        if XDG_SESSION_TYPE == 'wayland':
            return "wayland" if SettingsManager.get("system/wayland", False) else "xcb"

        logger.warning(
            f"""Plataforma '{XDG_SESSION_TYPE}'. Usando fallback '{SetupManager._qt_platform_xcb}'.""")
        return SetupManager._qt_platform_xcb
