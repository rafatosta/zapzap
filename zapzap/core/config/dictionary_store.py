"""Managed, writable storage used by the Qt WebEngine spellchecker."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import logging
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Iterable

from PyQt6.QtCore import QStandardPaths


logger = logging.getLogger(__name__)

SAFE_DICTIONARY_FILENAME = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.bdic$"
)


@dataclass(frozen=True)
class DictionaryStorePreparation:
    """Observable result of preparing the WebEngine dictionary directory."""

    path: str | None
    migrated: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    used_fallback: bool = False


class DictionaryStore:
    """Resolve and prepare one application-owned dictionary directory."""

    MIGRATION_VERSION = 1
    MAX_MANIFEST_BYTES = 2 * 1024 * 1024
    CATALOG_REPOSITORY = "rafatosta/qtwebengine_dictionaries"
    _path_override: Path | None = None

    @classmethod
    def set_path_override_for_tests(cls, path: str | Path | None) -> None:
        cls._path_override = Path(path) if path is not None else None

    @classmethod
    def path(cls) -> Path:
        if cls._path_override is not None:
            return cls._path_override
        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        if not location:
            raise OSError("Qt did not provide a writable application data path")
        return Path(location) / "dictionaries"

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        return bool(SAFE_DICTIONARY_FILENAME.fullmatch(filename or ""))

    @classmethod
    def is_dictionary_directory(
        cls,
        path: str | os.PathLike[str] | None,
    ) -> bool:
        """Return whether an existing directory provides usable dictionaries."""
        if not path:
            return False
        directory = Path(path)
        try:
            if directory.is_symlink() or not directory.is_dir():
                return False
            return any(
                cls.is_safe_filename(item.name)
                and item.is_file()
                and not item.is_symlink()
                for item in directory.iterdir()
            )
        except OSError:
            return False

    @classmethod
    def is_complete_dictionary_catalog(
        cls,
        path: str | os.PathLike[str] | None,
    ) -> bool:
        """Validate that a package directory matches its complete manifest."""
        if not cls.is_dictionary_directory(path):
            return False
        directory = Path(path)
        manifest = directory / "manifest.json"
        try:
            if manifest.is_symlink() or not manifest.is_file():
                return False
            if manifest.stat().st_size > cls.MAX_MANIFEST_BYTES:
                return False
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return False
            records = payload.get("dictionaries")
            if (
                payload.get("schema_version") != 1
                or payload.get("repository") != cls.CATALOG_REPOSITORY
                or not isinstance(payload.get("catalog_revision"), str)
                or not payload["catalog_revision"]
                or not isinstance(records, list)
            ):
                return False

            expected: dict[str, int] = {}
            for record in records:
                if not isinstance(record, dict):
                    return False
                filename = record.get("filename")
                size = record.get("size")
                if (
                    not isinstance(filename, str)
                    or not cls.is_safe_filename(filename)
                    or filename in expected
                    or not isinstance(size, int)
                    or size <= 0
                ):
                    return False
                expected[filename] = size
            if not expected:
                return False

            actual = {
                item.name: item.stat().st_size
                for item in directory.iterdir()
                if cls.is_safe_filename(item.name)
                and item.is_file()
                and not item.is_symlink()
            }
            return actual == expected
        except (OSError, UnicodeError, json.JSONDecodeError):
            return False

    @staticmethod
    def _digest(path: Path) -> str:
        hasher = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def _copy_atomic(
        cls,
        source: Path,
        destination: Path,
        *,
        replace: bool = False,
    ) -> bool:
        if source.is_symlink() or not source.is_file():
            raise ValueError("source is not a regular file")
        if not cls.is_safe_filename(source.name):
            raise ValueError("unsafe dictionary filename")
        if destination.is_symlink() or destination.exists():
            if destination.is_symlink() or not destination.is_file():
                raise ValueError("destination is not a regular file")
            if (
                destination.stat().st_size == source.stat().st_size
                and cls._digest(destination) == cls._digest(source)
            ):
                return False
            if not replace:
                raise FileExistsError("a different managed dictionary already exists")

        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=f".{source.stem}-",
                suffix=".part",
                dir=destination.parent,
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                with source.open("rb") as input_handle:
                    shutil.copyfileobj(input_handle, temporary, 1024 * 1024)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, destination)
            temporary_name = None
            return True
        finally:
            if temporary_name:
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass

    @classmethod
    def _migration_marker(cls, managed: Path) -> Path:
        return managed / ".zapzap" / "migration-v1.json"

    @staticmethod
    def _write_json_atomic(path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix=f".{path.stem}-",
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

    @classmethod
    def prepare(
        cls,
        legacy_paths: Iterable[str | os.PathLike[str] | None] = (),
    ) -> DictionaryStorePreparation:
        """Create the store and copy legacy dictionaries without changing sources."""
        candidates = []
        for raw_path in legacy_paths:
            if not raw_path:
                continue
            candidate = Path(raw_path).expanduser()
            if candidate not in candidates:
                candidates.append(candidate)

        try:
            managed = cls.path()
            managed.mkdir(parents=True, exist_ok=True)
            if managed.is_symlink() or not managed.is_dir():
                raise OSError("managed dictionary path is not a real directory")
        except OSError as error:
            logger.error("Unable to prepare managed dictionary store: %s", error)
            fallback = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate.is_dir() and not candidate.is_symlink()
                ),
                None,
            )
            return DictionaryStorePreparation(
                str(fallback) if fallback else None,
                failures=(str(error),),
                used_fallback=fallback is not None,
            )

        marker = cls._migration_marker(managed)
        if marker.is_file():
            return DictionaryStorePreparation(str(managed))

        migrated: list[str] = []
        failures: list[str] = []
        for source_root in candidates:
            try:
                if (
                    not source_root.is_dir()
                    or source_root.is_symlink()
                    or source_root.resolve() == managed.resolve()
                ):
                    continue
                for source in sorted(source_root.iterdir(), key=lambda item: item.name):
                    if not cls.is_safe_filename(source.name):
                        continue
                    try:
                        if cls._copy_atomic(source, managed / source.name):
                            migrated.append(source.name)
                    except (OSError, ValueError) as error:
                        failures.append(f"{source.name}: {error}")
            except OSError as error:
                failures.append(f"{source_root}: {error}")

        if not failures:
            cls._write_json_atomic(
                marker,
                {
                    "version": cls.MIGRATION_VERSION,
                    "migrated": sorted(migrated),
                },
            )
        if migrated:
            logger.info("Migrated %d dictionaries into managed storage", len(migrated))
        for failure in failures:
            logger.warning("Dictionary migration did not copy %s", failure)
        return DictionaryStorePreparation(
            str(managed), tuple(migrated), tuple(failures)
        )
