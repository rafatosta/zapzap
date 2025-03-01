import os
from PyQt6.QtCore import QLocale
from zapzap.services.EnvironmentManager import EnvironmentManager, Packaging
from zapzap.services.PathManager import PathManager
from zapzap.services.SettingsManager import SettingsManager


class DictionariesManager:
    """Gerencia os dicionários de linguagem do sistema."""

    @staticmethod
    def get_path() -> str:
        """
        Retorna o caminho configurado para os dicionários ou o caminho padrão
        """
        return PathManager.get_paths(EnvironmentManager.identify_packaging())['path']

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
    def set_spell_folder(path: str) -> str:
        """
        Configura o caminho personalizado para o diretório de dicionários.

        Args:
            path (str): Caminho para o diretório de dicionários.
        """
        PathManager.set_custom_path(
            EnvironmentManager.identify_packaging(), path)

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

    @staticmethod
    def restore_default_path() -> str:
        PathManager.restore_default_path(
            EnvironmentManager.identify_packaging())
        return DictionariesManager.get_path()
