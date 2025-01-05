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
        Retorna o caminho configurado para os dicionários ou o caminho padrão.
        """
        return SettingsManager.get(
            "spellcheck/folder", DictionariesManager.get_path_default()
        )

    @staticmethod
    def get_path_default() -> str:
        """
        Retorna o caminho padrão para os dicionários, dependendo do ambiente.
        """
        return (
            DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH_FLATPAK
            if SetupManager._is_flatpak
            else DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH
        )

    @staticmethod
    def list_files():
        """
        Exibe no console os idiomas disponíveis no diretório de dicionários.
        """
        dictionaries_path = DictionariesManager.get_path()
        if dictionaries_path and os.path.isdir(dictionaries_path):
            print("Linguagens disponíveis:")
            for file in os.listdir(dictionaries_path):
                if file.endswith(".bdic"):
                    print(file.replace(".bdic", ""))
        else:
            print("Caminho de dicionários não encontrado ou inválido.")

    @staticmethod
    def list() -> list:
        """
        Retorna uma lista com os idiomas disponíveis no diretório de dicionários.

        Returns:
            list: Lista de idiomas disponíveis.
        """
        dictionaries_path = DictionariesManager.get_path()
        if dictionaries_path and os.path.isdir(dictionaries_path):
            return [
                file.replace(".bdic", "")
                for file in os.listdir(dictionaries_path)
                if file.endswith(".bdic")
            ]
        print("Caminho de dicionários não encontrado ou inválido.")
        return []

    @staticmethod
    def set_lang(lang: str):
        """
        Define o idioma atual para o corretor ortográfico.

        Args:
            lang (str): Idioma a ser configurado.
        """
        SettingsManager.set("system/spellCheckLanguage", lang)

    @staticmethod
    def set_spell_folder(path: str):
        """
        Configura o caminho personalizado para o diretório de dicionários.

        Args:
            path (str): Caminho para o diretório de dicionários.
        """
        SettingsManager.set("spellcheck/folder", path)

    @staticmethod
    def get_current_dict() -> str:
        """
        Retorna o idioma atualmente configurado para o corretor ortográfico.

        Returns:
            str: Idioma atual configurado.
        """
        return SettingsManager.get(
            "system/spellCheckLanguage", DictionariesManager.get_system_language()
        )

    @staticmethod
    def get_system_language() -> str:
        """
        Retorna o idioma padrão do sistema.

        Returns:
            str: Idioma padrão do sistema (exemplo: 'en_US').
        """
        return QLocale.system().name()
