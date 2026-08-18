"""Validated remote catalog and offline cache for WebEngine dictionaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote

from PyQt6.QtCore import QStandardPaths

from zapzap.core.config.dictionary_store import DictionaryStore


MAX_CATALOG_BYTES = 2 * 1024 * 1024
MAX_DICTIONARIES = 1000
MAX_DICTIONARY_BYTES = 64 * 1024 * 1024
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
GIT_SHA_PATTERN = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class DictionaryCatalogEntry:
    code: str
    filename: str
    size: int
    source_revision: str
    source: str
    qt_version: str | None = None
    sha256: str | None = None
    git_sha: str | None = None

    @property
    def download_url(self) -> str:
        filename = quote(self.filename, safe="._-")
        return (
            "https://raw.githubusercontent.com/"
            "rafatosta/qtwebengine_dictionaries/"
            f"{self.source_revision}/{filename}"
        )


@dataclass(frozen=True)
class DictionaryCatalogSnapshot:
    entries: tuple[DictionaryCatalogEntry, ...]
    revision: str
    fetched_at: str
    stale: bool = False
    source: str = "manifest"
    etag: str = ""


def _require_string(value, field: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(f"invalid catalog field: {field}")
    return value


def parse_manifest(payload: bytes) -> DictionaryCatalogSnapshot:
    if len(payload) > MAX_CATALOG_BYTES:
        raise ValueError("dictionary manifest is too large")
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("unsupported dictionary manifest schema")
    records = data.get("dictionaries")
    if (
        not isinstance(records, list)
        or not records
        or len(records) > MAX_DICTIONARIES
    ):
        raise ValueError("invalid dictionary manifest entry count")

    entries: list[DictionaryCatalogEntry] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("dictionary manifest entry is not an object")
        filename = _require_string(record.get("filename"), "filename", 160)
        code = _require_string(record.get("code"), "code", 154)
        if (
            not DictionaryStore.is_safe_filename(filename)
            or code != filename.removesuffix(".bdic")
            or filename in seen
        ):
            raise ValueError(f"unsafe or duplicate dictionary: {filename}")
        seen.add(filename)
        size = record.get("size")
        if not isinstance(size, int) or not 0 < size <= MAX_DICTIONARY_BYTES:
            raise ValueError(f"invalid dictionary size: {filename}")
        digest = _require_string(record.get("sha256"), "sha256", 64)
        if not SHA256_PATTERN.fullmatch(digest):
            raise ValueError(f"invalid SHA-256: {filename}")
        revision = _require_string(
            record.get("source_revision"), "source_revision", 40
        )
        if not GIT_SHA_PATTERN.fullmatch(revision):
            raise ValueError(f"invalid source revision: {filename}")
        qt_version = record.get("qt_version")
        if qt_version is not None and (
            not isinstance(qt_version, str) or len(qt_version) > 32
        ):
            raise ValueError(f"invalid Qt version: {filename}")
        entries.append(
            DictionaryCatalogEntry(
                code=code,
                filename=filename,
                size=size,
                sha256=digest,
                source_revision=revision,
                source=_require_string(record.get("source"), "source"),
                qt_version=qt_version,
            )
        )
    return DictionaryCatalogSnapshot(
        entries=tuple(entries),
        revision=_require_string(data.get("catalog_revision"), "catalog_revision"),
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )


def parse_github_tree(
    payload: bytes,
    *,
    commit_revision: str,
) -> DictionaryCatalogSnapshot:
    if len(payload) > MAX_CATALOG_BYTES:
        raise ValueError("GitHub tree response is too large")
    if not GIT_SHA_PATTERN.fullmatch(commit_revision):
        raise ValueError("invalid GitHub commit revision")
    data = json.loads(payload.decode("utf-8"))
    records = data.get("tree") if isinstance(data, dict) else None
    if (
        not isinstance(records, list)
        or data.get("truncated") is True
        or len(records) > MAX_DICTIONARIES + 32
    ):
        raise ValueError("invalid or truncated GitHub tree")
    entries = []
    seen = set()
    for record in records:
        if not isinstance(record, dict) or record.get("type") != "blob":
            continue
        filename = record.get("path")
        if not isinstance(filename, str) or "/" in filename:
            continue
        if not DictionaryStore.is_safe_filename(filename):
            continue
        size = record.get("size")
        git_sha = record.get("sha")
        if (
            filename in seen
            or not isinstance(size, int)
            or not 0 < size <= MAX_DICTIONARY_BYTES
            or not isinstance(git_sha, str)
            or not GIT_SHA_PATTERN.fullmatch(git_sha)
        ):
            raise ValueError(f"invalid GitHub dictionary entry: {filename}")
        seen.add(filename)
        entries.append(
            DictionaryCatalogEntry(
                code=filename.removesuffix(".bdic"),
                filename=filename,
                size=size,
                source_revision=commit_revision,
                source="github-tree-fallback",
                git_sha=git_sha,
            )
        )
    if not entries:
        raise ValueError("GitHub tree contains no dictionaries")
    return DictionaryCatalogSnapshot(
        entries=tuple(entries),
        revision=commit_revision,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        source="github-tree",
    )


class DictionaryCatalogCache:
    """Atomically persist the last validated catalog for offline use."""

    def __init__(self, directory: str | Path | None = None):
        if directory is None:
            base = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.CacheLocation
            )
            if not base:
                raise OSError("Qt did not provide a cache directory")
            directory = Path(base) / "dictionaries"
        self.directory = Path(directory)
        self.path = self.directory / "catalog.json"

    def save(self, snapshot: DictionaryCatalogSnapshot) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": 1,
            "revision": snapshot.revision,
            "fetched_at": snapshot.fetched_at,
            "source": snapshot.source,
            "etag": snapshot.etag,
            "entries": [asdict(entry) for entry in snapshot.entries],
        }
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix=".catalog-",
                suffix=".json",
                dir=self.directory,
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                json.dump(data, temporary, indent=2, sort_keys=True)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, self.path)
            temporary_name = None
        finally:
            if temporary_name:
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass

    def load(self) -> DictionaryCatalogSnapshot | None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return None
        try:
            if not isinstance(data, dict):
                return None
            if data.get("schema_version") != 1:
                return None
            records = data["entries"]
            if not isinstance(records, list) or len(records) > MAX_DICTIONARIES:
                return None
            entries = tuple(DictionaryCatalogEntry(**record) for record in records)
            seen = set()
            for entry in entries:
                if (
                    not DictionaryStore.is_safe_filename(entry.filename)
                    or entry.code != entry.filename.removesuffix(".bdic")
                    or entry.filename in seen
                    or not 0 < entry.size <= MAX_DICTIONARY_BYTES
                    or not GIT_SHA_PATTERN.fullmatch(entry.source_revision)
                    or not isinstance(entry.source, str)
                    or not entry.source
                ):
                    return None
                seen.add(entry.filename)
                if entry.sha256 and not SHA256_PATTERN.fullmatch(entry.sha256):
                    return None
                if entry.git_sha and not GIT_SHA_PATTERN.fullmatch(entry.git_sha):
                    return None
                if not entry.sha256 and not entry.git_sha:
                    return None
            return DictionaryCatalogSnapshot(
                entries=entries,
                revision=_require_string(data["revision"], "revision"),
                fetched_at=_require_string(data["fetched_at"], "fetched_at"),
                stale=True,
                source=_require_string(data.get("source", "cache"), "source"),
                etag=data.get("etag", "") if isinstance(data.get("etag", ""), str) else "",
            )
        except (AttributeError, KeyError, TypeError, ValueError):
            return None

    def with_etag(
        self,
        snapshot: DictionaryCatalogSnapshot,
        etag: str,
    ) -> DictionaryCatalogSnapshot:
        return replace(snapshot, etag=etag)

    def mark_fresh(
        self,
        snapshot: DictionaryCatalogSnapshot,
    ) -> DictionaryCatalogSnapshot:
        return replace(
            snapshot,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            stale=False,
        )
