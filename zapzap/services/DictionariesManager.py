import os
from PyQt6.QtCore import QLocale
from zapzap.config.SetupManager import SetupManager
from zapzap.services.SettingsManager import SettingsManager


class DictionariesManager:
    """Gerencia os dicionários de linguagem do sistema."""

    QTWEBENGINE_DICTIONARIES_PATH = "/usr/share/qt6/qtwebengine_dictionaries"
    QTWEBENGINE_DICTIONARIES_PATH_FLATPAK = "/run/host/usr/share/qt6/qtwebengine_dictionaries"

    @staticmethod
    def get_path() -> str:
        """
        Retorna o caminho para os dicionários, dependendo do ambiente de execução.
        """
        return (
            DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH_FLATPAK
            if SetupManager._is_flatpak
            else DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH
        )

    @staticmethod
    def list_files():
        """
        Exibe os idiomas disponíveis no console.
        """
        dictionaries_path = DictionariesManager.get_path()
        if dictionaries_path and os.path.isdir(dictionaries_path):
            print("Linguagens disponíveis:")
            for file in os.listdir(dictionaries_path):
                if file.endswith(".bdic"):
                    print(file.replace(".bdic", ""))
        else:
            print("Caminho não encontrado ou inválido.")

    @staticmethod
    def list() -> list:
        """
        Retorna uma lista de idiomas disponíveis.
        """
        dict_list = []
        dictionaries_path = DictionariesManager.get_path()
        if dictionaries_path and os.path.isdir(dictionaries_path):
            dict_list = [
                file.replace(".bdic", "")
                for file in os.listdir(dictionaries_path)
                if file.endswith(".bdic")
            ]
        else:
            print("Caminho não encontrado ou inválido.")
        return dict_list

    @staticmethod
    def set_lang(lang: str):
        """
        Define o idioma atual para o corretor ortográfico.
        """
        SettingsManager.set("system/spellCheckLanguage", lang)

    @staticmethod
    def get_current_dict() -> str:
        """
        Retorna o idioma atualmente configurado para o corretor ortográfico.
        """
        return SettingsManager.get(
            "system/spellCheckLanguage", DictionariesManager.get_system_language()
        )

    @staticmethod
    def get_system_language() -> str:
        """
        Retorna o idioma padrão do sistema.
        """
        return QLocale.system().name()
