from zapzap.services.EnvironmentManager import Packaging
from zapzap.services.SettingsManager import SettingsManager
import os


class PathManager:
    # Dicionário contendo os caminhos para cada ambiente
    paths = {
        Packaging.APPIMAGE: {
            "path": "",
            "default": os.path.join(os.getenv("APPDIR", "/"), "qtwebengine_dictionaries"),
        },
        Packaging.FLATPAK: {
            "path": "",
            "default": os.getenv("QTWEBENGINE_DICTIONARIES_PATH", ""),
        },
        Packaging.RPM: {
            "path": "",
            "default": "/usr/share/qt6/qtwebengine_dictionaries",
        },
        Packaging.UNOFFICIAL: {
            "path": "",
            "default": "/usr/share/qt6/qtwebengine_dictionaries",
        }
    }

    @staticmethod
    def get_paths(packaging_type):
        """Retorna os caminhos, considerando o caminho customizado ou o padrão."""
        paths = PathManager.paths.get(packaging_type, None)
        if paths:
            # Obtém o caminho customizado, se existir, ou o caminho padrão
            path = SettingsManager.get(
                f"spellcheck/folder_{packaging_type.value}", paths["default"])
            if path:
                paths["path"] = path  # Substitui o caminho do dicionário
            return paths
        return None

    @staticmethod
    def show_paths(packaging_type):
        """Exibe os caminhos no formato ilustrativo para o usuário."""
        paths = PathManager.get_paths(packaging_type)
        if paths:
            print(f"Caminho: {paths['path']}")
            print(f"Caminho Padrão: {paths['default']}")
            print(f"Caminho Ilustrativo: {paths['user_friendly']}")
        else:
            print("Tipo de empacotamento não encontrado.")

    @staticmethod
    def set_custom_path(packaging_type, new_path):
        """Altera o caminho customizado e armazena no SettingsManager."""
        SettingsManager.set(
            f"""spellcheck/folder_{packaging_type.value}""", new_path)
        print(
            f"""Caminho customizado para {packaging_type.value} alterado para: {new_path}""")

    @staticmethod
    def restore_default_path(packaging_type):
        """Restaura o caminho para o padrão removendo o customizado."""
        SettingsManager.remove(f"spellcheck/folder_{packaging_type.value}")
        print(
            f"""Restaura caminho customizado para {packaging_type.value} restaurado para o padrão.""")
