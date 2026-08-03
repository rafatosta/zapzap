from __future__ import annotations

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

    MAX_SELECTED_LANGUAGES = 10
    MAX_RECENT_LANGUAGES = 4
    _SELECTED_LANGUAGES_KEY = "system/spellCheckLanguages"
    _LEGACY_LANGUAGE_KEY = "system/spellCheckLanguage"
    _RECENT_LANGUAGES_KEY = "system/recentSpellCheckLanguages"

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
        DictionariesManager.set_selected_languages([lang])

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
        selected = DictionariesManager.get_selected_languages()
        return selected[0] if selected else DictionariesManager.get_system_language()

    @staticmethod
    def _as_list(value) -> list[str]:
        """Return QSettings scalar/list values as a clean string list."""
        if isinstance(value, str):
            values = [value]
        elif isinstance(value, (list, tuple)):
            values = value
        else:
            values = []
        return [str(item) for item in values if str(item).strip()]

    @staticmethod
    def _normalize_languages(
        languages,
        installed: list[str] | None = None,
        limit: int | None = None,
    ) -> list[str]:
        """Deduplicate and validate dictionary codes without changing order."""
        if installed is None:
            installed = [option.code for option in DictionariesManager.options()]
        installed_codes = set(installed)
        maximum = limit or DictionariesManager.MAX_SELECTED_LANGUAGES
        normalized = []
        for code in DictionariesManager._as_list(languages):
            if code not in installed_codes or code in normalized:
                continue
            normalized.append(code)
            if len(normalized) >= maximum:
                break
        return normalized

    @staticmethod
    def _fallback_language(installed: list[str]) -> str | None:
        """Choose the installed dictionary closest to the system locale."""
        if not installed:
            return None
        system_code = DictionariesManager.get_system_language()
        if system_code in installed:
            return system_code
        system_language = QLocale(system_code).language()
        for code in installed:
            locale_name = DictionariesManager._LOCALE_ASSOCIATIONS.get(code, code)
            if QLocale(locale_name).language() == system_language:
                return code
        return installed[0]

    @staticmethod
    def get_selected_languages() -> list[str]:
        """Return the normalized selection, migrating the legacy scalar key.

        The legacy key remains in place and is kept synchronized so downgrading
        ZapZap still leaves a usable primary dictionary.
        """
        installed = [option.code for option in DictionariesManager.options()]
        if not installed:
            return []

        selected = []
        if SettingsManager.contains(DictionariesManager._SELECTED_LANGUAGES_KEY):
            selected = DictionariesManager._normalize_languages(
                SettingsManager.get(DictionariesManager._SELECTED_LANGUAGES_KEY, []),
                installed,
            )
        if not selected:
            legacy = SettingsManager.get(
                DictionariesManager._LEGACY_LANGUAGE_KEY,
                DictionariesManager.get_system_language(),
            )
            selected = DictionariesManager._normalize_languages([legacy], installed)
        if not selected:
            fallback = DictionariesManager._fallback_language(installed)
            selected = [fallback] if fallback else []

        SettingsManager.set(DictionariesManager._SELECTED_LANGUAGES_KEY, selected)
        if selected:
            SettingsManager.set(DictionariesManager._LEGACY_LANGUAGE_KEY, selected[0])
        return selected

    @staticmethod
    def set_selected_languages(languages: list[str]) -> None:
        """Persist a valid global selection of at most ten dictionaries."""
        installed = [option.code for option in DictionariesManager.options()]
        selected = DictionariesManager._normalize_languages(languages, installed)
        if not selected:
            fallback = DictionariesManager._fallback_language(installed)
            selected = [fallback] if fallback else []
        SettingsManager.set(DictionariesManager._SELECTED_LANGUAGES_KEY, selected)
        if selected:
            SettingsManager.set(DictionariesManager._LEGACY_LANGUAGE_KEY, selected[0])

    @staticmethod
    def get_recent_languages() -> list[str]:
        """Return installed recent dictionaries, newest first."""
        installed = [option.code for option in DictionariesManager.options()]
        recent = DictionariesManager._normalize_languages(
            SettingsManager.get(DictionariesManager._RECENT_LANGUAGES_KEY, []),
            installed,
            DictionariesManager.MAX_RECENT_LANGUAGES,
        )
        SettingsManager.set(DictionariesManager._RECENT_LANGUAGES_KEY, recent)
        return recent

    @staticmethod
    def update_recent_languages(languages: list[str]) -> None:
        """Move the supplied installed dictionaries to the front of recents."""
        existing = DictionariesManager.get_recent_languages()
        combined = DictionariesManager._as_list(languages) + existing
        installed = [option.code for option in DictionariesManager.options()]
        recent = DictionariesManager._normalize_languages(
            combined,
            installed,
            DictionariesManager.MAX_RECENT_LANGUAGES,
        )
        SettingsManager.set(DictionariesManager._RECENT_LANGUAGES_KEY, recent)

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
