import os

from zapzap.config.SetupManager import SetupManager


class DictionariesManager:
    """Gerencia os dicionários """

    QTWEBENGINE_DICTIONARIES_PATH = "/usr/share/qt6/qtwebengine_dictionaries"

    QTWEBENGINE_DICTIONARIES_PATH_FLATPAK = "/run/host/usr/share/qt6/qtwebengine_dictionaries"

    @staticmethod
    def list_files():
        dictionaries_path = DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH
        if dictionaries_path and os.path.isdir(dictionaries_path):
            print("Linguagens disponíveis:")
            for file in os.listdir(dictionaries_path):
                if file.endswith(".bdic"):
                    print(file.replace(".bdic", ""))
        else:
            print("Caminho não encontrado ou inválido.")

    @staticmethod
    def get_path():
        if SetupManager._is_flatpak:
            return DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH_FLATPAK

        return DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH
