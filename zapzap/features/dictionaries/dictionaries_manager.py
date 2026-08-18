from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import logging
import os
from pathlib import Path
import re
import shutil
import tempfile

from PyQt6.QtCore import QLocale

from zapzap.core.config.dictionary_store import DictionaryStore
from zapzap.core.config.settings.spellcheck import SpellcheckSettings
from zapzap.core.config.settings_manager import SettingsManager


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DictionaryOption:
    """A dictionary identifier and its human-readable presentation label."""

    code: str
    label: str


class DictionaryError(str, Enum):
    NONE = "none"
    INVALID_FILE = "invalid_file"
    CONFLICT = "conflict"
    PERMISSION = "permission"
    DISK_FULL = "disk_full"
    LAST_ACTIVE = "last_active"
    NOT_INSTALLED = "not_installed"
    CANCELLED = "cancelled"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    HTTP = "http"
    REDIRECT = "redirect"
    SIZE = "size"
    HASH = "hash"
    BUSY = "busy"


@dataclass(frozen=True)
class DictionaryOperationResult:
    success: bool
    code: str = ""
    error: DictionaryError = DictionaryError.NONE
    detail: str = ""


@dataclass(frozen=True)
class DictionaryState:
    code: str
    label: str
    installed: bool
    active: bool
    local: bool
    available: bool
    transferring: bool = False
    progress: int = 0
    error: DictionaryError = DictionaryError.NONE
    restart_required: bool = False


class DictionariesManager:
    """Gerencia os dicionários de linguagem do sistema."""

    MAX_SELECTED_LANGUAGES = 10
    MAX_RECENT_LANGUAGES = 4
    _SELECTED_LANGUAGES_KEY = "system/spellCheckLanguages"
    _LEGACY_LANGUAGE_KEY = "system/spellCheckLanguage"
    _RECENT_LANGUAGES_KEY = "system/recentSpellCheckLanguages"
    _METADATA_DIRECTORY = ".zapzap"
    _METADATA_FILE = "installed.json"

    # Some distributed dictionaries append a format/version suffix that is not
    # part of the locale identifier. Keep these associations presentation-only:
    # the original filename stem must still be passed to Qt WebEngine.
    _LOCALE_ASSOCIATIONS = {
        "es-ES-3-0": "es_ES",
    }

    @staticmethod
    def get_path() -> str:
        """Return the single application-owned dictionary directory."""
        return str(DictionaryStore.path())

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
            return sorted(
                file.removesuffix(".bdic")
                for file in os.listdir(dictionaries_path)
                if DictionaryStore.is_safe_filename(file)
                and os.path.isfile(os.path.join(dictionaries_path, file))
                and not os.path.islink(os.path.join(dictionaries_path, file))
            )
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
        """Compatibility wrapper: import dictionaries instead of changing roots."""
        DictionariesManager.import_directory(path)
        return DictionariesManager.get_path()

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
        """Compatibility wrapper for the now permanent managed directory."""
        return DictionariesManager.get_path()

    @staticmethod
    def _metadata_path() -> Path:
        return (
            Path(DictionariesManager.get_path())
            / DictionariesManager._METADATA_DIRECTORY
            / DictionariesManager._METADATA_FILE
        )

    @staticmethod
    def _load_metadata() -> dict:
        path = DictionariesManager._metadata_path()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return {"schema_version": 1, "dictionaries": {}}
        if not isinstance(value, dict) or not isinstance(
            value.get("dictionaries"), dict
        ):
            return {"schema_version": 1, "dictionaries": {}}
        return value

    @staticmethod
    def _save_metadata(value: dict) -> None:
        path = DictionariesManager._metadata_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix=".installed-",
                suffix=".json",
                dir=path.parent,
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                json.dump(value, temporary, indent=2, sort_keys=True)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, path)
            temporary_name = None
        finally:
            if temporary_name:
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass

    @staticmethod
    def record_install(code: str, metadata: dict) -> None:
        """Record provenance after a verified file has been committed."""
        if not DictionaryStore.is_safe_filename(f"{code}.bdic"):
            raise ValueError("unsafe dictionary code")
        value = DictionariesManager._load_metadata()
        record = dict(metadata)
        record.setdefault("installed_at", datetime.now(timezone.utc).isoformat())
        value["dictionaries"][code] = record
        DictionariesManager._save_metadata(value)

    @staticmethod
    def import_file(
        path: str | os.PathLike[str],
        *,
        replace: bool = False,
    ) -> DictionaryOperationResult:
        source = Path(path)
        code = source.stem
        if not DictionaryStore.is_safe_filename(source.name):
            return DictionaryOperationResult(
                False, code, DictionaryError.INVALID_FILE, "invalid .bdic filename"
            )
        destination = Path(DictionariesManager.get_path()) / source.name
        copied = False
        backup_name = None
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if replace and (
                destination.is_symlink()
                or (destination.exists() and not destination.is_file())
            ):
                raise ValueError("destination is not a regular file")
            if replace and destination.exists():
                with tempfile.NamedTemporaryFile(
                    prefix=f".{destination.stem}-",
                    suffix=".backup",
                    dir=destination.parent,
                    delete=False,
                ) as backup:
                    backup_name = backup.name
                    with destination.open("rb") as installed:
                        shutil.copyfileobj(installed, backup, 1024 * 1024)
                    backup.flush()
                    os.fsync(backup.fileno())
            copied = DictionaryStore._copy_atomic(
                source,
                destination,
                replace=replace,
            )
            DictionariesManager.record_install(
                code,
                {
                    "source": "local",
                    "source_filename": source.name,
                    "size": destination.stat().st_size,
                },
            )
            if backup_name:
                try:
                    os.unlink(backup_name)
                except OSError:
                    logger.warning("Could not remove a dictionary replacement backup")
                finally:
                    backup_name = None
            return DictionaryOperationResult(True, code)
        except FileExistsError as error:
            return DictionaryOperationResult(
                False, code, DictionaryError.CONFLICT, str(error)
            )
        except (OSError, ValueError) as error:
            if copied:
                try:
                    if backup_name:
                        os.replace(backup_name, destination)
                        backup_name = None
                    else:
                        destination.unlink()
                except OSError:
                    logger.warning(
                        "Could not roll back dictionary import after metadata failure"
                    )
            return DictionaryOperationResult(
                False, code, DictionaryError.PERMISSION, str(error)
            )
        finally:
            if backup_name:
                try:
                    os.unlink(backup_name)
                except FileNotFoundError:
                    pass

    @staticmethod
    def import_directory(path: str | os.PathLike[str]) -> list[DictionaryOperationResult]:
        root = Path(path)
        try:
            candidates = sorted(root.iterdir(), key=lambda item: item.name)
        except OSError as error:
            return [
                DictionaryOperationResult(
                    False, error=DictionaryError.PERMISSION, detail=str(error)
                )
            ]
        return [
            DictionariesManager.import_file(candidate)
            for candidate in candidates
            if DictionaryStore.is_safe_filename(candidate.name)
        ]

    @staticmethod
    def remove(
        code: str,
        *,
        disable_if_last: bool = False,
    ) -> DictionaryOperationResult:
        filename = f"{code}.bdic"
        if not DictionaryStore.is_safe_filename(filename):
            return DictionaryOperationResult(
                False, code, DictionaryError.INVALID_FILE, "unsafe dictionary code"
            )
        path = Path(DictionariesManager.get_path()) / filename
        try:
            if path.is_symlink():
                return DictionaryOperationResult(
                    False, code, DictionaryError.INVALID_FILE, "symbolic links are rejected"
                )
            if not path.exists():
                return DictionaryOperationResult(True, code)
            if not path.is_file():
                return DictionaryOperationResult(
                    False, code, DictionaryError.INVALID_FILE, "not a regular file"
                )
        except OSError as error:
            return DictionaryOperationResult(
                False, code, DictionaryError.PERMISSION, str(error)
            )

        selected = DictionariesManager.get_selected_languages()
        remaining_installed = [item for item in DictionariesManager.list() if item != code]
        removes_last_active = code in selected and not [
            item for item in selected if item != code and item in remaining_installed
        ]
        if removes_last_active and SpellcheckSettings().enabled and not disable_if_last:
            return DictionaryOperationResult(
                False,
                code,
                DictionaryError.LAST_ACTIVE,
                "the enabled spell checker needs an active dictionary",
            )

        try:
            path.unlink()
        except OSError as error:
            return DictionaryOperationResult(
                False, code, DictionaryError.PERMISSION, str(error)
            )

        if removes_last_active and disable_if_last:
            SpellcheckSettings().enabled = False
        DictionariesManager.set_selected_languages(
            [item for item in selected if item != code]
        )
        value = DictionariesManager._load_metadata()
        value["dictionaries"].pop(code, None)
        DictionariesManager._save_metadata(value)
        return DictionaryOperationResult(True, code)

    @staticmethod
    def states(catalog=()) -> list[DictionaryState]:
        installed = set(DictionariesManager.list())
        active = set(DictionariesManager.get_selected_languages())
        metadata = DictionariesManager._load_metadata().get("dictionaries", {})
        catalog_codes = {entry.code for entry in catalog}
        all_codes = installed | catalog_codes
        return sorted(
            (
                DictionaryState(
                    code=code,
                    label=DictionariesManager.label(code),
                    installed=code in installed,
                    active=code in active,
                    local=(
                        code in installed
                        and (
                            code not in catalog_codes
                            or metadata.get(code, {}).get("source") == "local"
                        )
                    ),
                    available=code in catalog_codes,
                )
                for code in all_codes
            ),
            key=lambda state: (state.label.casefold(), state.code.casefold()),
        )
