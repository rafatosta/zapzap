from dataclasses import dataclass
import os
import re

from PyQt6.QtCore import QLocale

from zapzap.core.environment.environment_manager import EnvironmentManager
from zapzap.core.config.path_manager import PathManager
from zapzap.core.config.settings_manager import SettingsManager


@dataclass(frozen=True)
class DictionaryOption:
    """A dictionary identifier and its human-readable presentation label."""

    code: str
    label: str


class DictionariesManager:
    """Gerencia os dicionários de linguagem do sistema."""

    # Some distributed dictionaries append a format/version suffix that is not
    # part of the locale identifier. Keep these associations presentation-only:
    # the original filename stem must still be passed to Qt WebEngine.
    _LOCALE_ASSOCIATIONS = {
        "es-ES-3-0": "es_ES",
    }

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
    def options() -> list[DictionaryOption]:
        """Return installed dictionaries with readable, alphabetical labels.

        The filename stem remains the stable value. Unknown custom dictionary
        names are deliberately kept visible instead of being filtered out.
        """
        options = [
            DictionaryOption(code, DictionariesManager.label(code))
            for code in DictionariesManager.list()
        ]
        return sorted(
            options,
            key=lambda option: (option.label.casefold(), option.code.casefold()),
        )

    @staticmethod
    def label(code: str) -> str:
        """Build a human-readable label without changing ``code``."""
        locale_name = DictionariesManager._LOCALE_ASSOCIATIONS.get(code, code)
        locale = QLocale(locale_name)
        if locale.language() == QLocale.Language.C:
            return code

        language_name = QLocale.languageToString(locale.language())
        details = []
        tokens = [token for token in re.split(r"[-_]", locale_name) if token]

        has_explicit_script = any(
            len(token) == 4 and token.isalpha() for token in tokens[1:]
        )
        if has_explicit_script:
            script_name = QLocale.scriptToString(locale.script())
            if script_name:
                details.append(script_name)

        has_explicit_territory = any(
            (len(token) == 2 and token.isalpha())
            or (len(token) == 3 and token.isdigit())
            for token in tokens[1:]
        )
        if has_explicit_territory:
            territory_name = QLocale.territoryToString(locale.territory())
            if territory_name:
                details.append(territory_name)

        if details:
            return f"{language_name} ({', '.join(details)})"
        return language_name

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
