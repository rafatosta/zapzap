"""Asynchronous network boundary for dictionary catalogs and downloads."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
import json
from pathlib import Path
from urllib.parse import unquote

from PyQt6.QtCore import QIODevice, QObject, QSaveFile, QUrl, pyqtSignal
from PyQt6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkReply,
    QNetworkRequest,
)

from zapzap.core.config.dictionary_store import DictionaryStore
from zapzap.features.dictionaries.dictionaries_manager import (
    DictionaryError,
    DictionaryOperationResult,
)
from zapzap.features.dictionaries.dictionary_catalog import (
    DictionaryCatalogCache,
    DictionaryCatalogEntry,
    GIT_SHA_PATTERN,
    MAX_CATALOG_BYTES,
    parse_github_tree,
    parse_manifest,
)


MANIFEST_URL = (
    "https://raw.githubusercontent.com/rafatosta/"
    "qtwebengine_dictionaries/main/manifest.json"
)
COMMIT_URL = (
    "https://api.github.com/repos/rafatosta/"
    "qtwebengine_dictionaries/commits/main"
)
TREE_URL_PREFIX = (
    "https://api.github.com/repos/rafatosta/"
    "qtwebengine_dictionaries/git/trees/"
)


@dataclass
class _Download:
    entry: DictionaryCatalogEntry
    reply: QNetworkReply
    output: QSaveFile
    sha256_hash: object
    git_hash: object
    received: int = 0
    cancelled: bool = False
    failed: DictionaryOperationResult | None = None


class DictionaryService(QObject):
    """Fetch a validated catalog and install at most two files concurrently."""

    catalog_loaded = pyqtSignal(object)
    catalog_failed = pyqtSignal(str, bool)
    download_progress = pyqtSignal(str, int, int)
    download_finished = pyqtSignal(str, object)

    MAX_CONCURRENT_DOWNLOADS = 2
    TRANSFER_TIMEOUT_MS = 15_000

    def __init__(
        self,
        parent=None,
        *,
        network: QNetworkAccessManager | None = None,
        cache: DictionaryCatalogCache | None = None,
        destination: str | Path | None = None,
    ):
        super().__init__(parent)
        self.network = network or QNetworkAccessManager(self)
        self.cache = cache or DictionaryCatalogCache()
        self.destination = Path(destination or DictionaryStore.path())
        self._catalog_reply: QNetworkReply | None = None
        self._downloads: dict[str, _Download] = {}
        self._pending: dict[str, DictionaryCatalogEntry] = {}
        self._fallback_commit = ""
        self._closing = False

    @staticmethod
    def _request(url: str) -> QNetworkRequest:
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", b"ZapZap-dictionary-manager")
        request.setAttribute(
            QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
        )
        if hasattr(request, "setTransferTimeout"):
            request.setTransferTimeout(DictionaryService.TRANSFER_TIMEOUT_MS)
        return request

    @staticmethod
    def _valid_final_url(url: QUrl, *, expected_filename: str | None = None) -> bool:
        if url.scheme() != "https":
            return False
        host = url.host().casefold()
        path = unquote(url.path())
        if host == "raw.githubusercontent.com":
            prefix = "/rafatosta/qtwebengine_dictionaries/"
            if not path.startswith(prefix):
                return False
            tail = path[len(prefix):].split("/")
            if expected_filename is None:
                return tail == ["main", "manifest.json"]
            return (
                len(tail) == 2
                and bool(GIT_SHA_PATTERN.fullmatch(tail[0]))
                and tail[1] == expected_filename
                and DictionaryStore.is_safe_filename(tail[1])
            )
        if host == "api.github.com":
            prefix = "/repos/rafatosta/qtwebengine_dictionaries/"
            tail = path.removeprefix(prefix)
            return path.startswith(prefix) and (
                tail == "commits/main"
                or (
                    tail.startswith("git/trees/")
                    and bool(GIT_SHA_PATTERN.fullmatch(tail.removeprefix("git/trees/")))
                )
            )
        return False

    @staticmethod
    def _status(reply: QNetworkReply) -> int:
        value = reply.attribute(
            QNetworkRequest.Attribute.HttpStatusCodeAttribute
        )
        return int(value) if value is not None else 0

    @staticmethod
    def _read_limited(reply: QNetworkReply, maximum: int) -> bytes:
        result = bytearray()
        while reply.bytesAvailable():
            chunk = bytes(reply.read(min(64 * 1024, maximum + 1 - len(result))))
            result.extend(chunk)
            if len(result) > maximum:
                raise ValueError("network response exceeds its size limit")
        return bytes(result)

    def fetch_catalog(self, *, force: bool = False) -> None:
        if self._catalog_reply is not None:
            return
        request = self._request(MANIFEST_URL)
        cached = self.cache.load()
        if cached and cached.etag and not force:
            request.setRawHeader(b"If-None-Match", cached.etag.encode("latin-1"))
        reply = self.network.get(request)
        self._catalog_reply = reply
        reply.finished.connect(lambda: self._manifest_finished(reply))

    def _manifest_finished(self, reply: QNetworkReply) -> None:
        if reply is not self._catalog_reply:
            return
        self._catalog_reply = None
        status = self._status(reply)
        if status == 304:
            cached = self.cache.load()
            reply.deleteLater()
            if cached:
                cached = self.cache.mark_fresh(cached)
                try:
                    self.cache.save(cached)
                except OSError as error:
                    self.catalog_loaded.emit(cached)
                    self.catalog_failed.emit(str(error), True)
                    return
                self.catalog_loaded.emit(cached)
            else:
                self._start_tree_fallback()
            return
        if status == 200 and self._valid_final_url(reply.url()):
            try:
                payload = self._read_limited(reply, MAX_CATALOG_BYTES)
                snapshot = parse_manifest(payload)
                etag = bytes(reply.rawHeader(b"ETag")).decode("latin-1")
                snapshot = self.cache.with_etag(snapshot, etag)
                self.cache.save(snapshot)
            except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as error:
                reply.deleteLater()
                self._catalog_failure(str(error))
                return
            reply.deleteLater()
            self.catalog_loaded.emit(snapshot)
            return
        reply.deleteLater()
        if status in (0, 404):
            self._start_tree_fallback()
        else:
            self._catalog_failure(self._http_detail(status))

    def _start_tree_fallback(self) -> None:
        if self._catalog_reply is not None:
            return
        reply = self.network.get(self._request(COMMIT_URL))
        self._catalog_reply = reply
        reply.finished.connect(lambda: self._commit_finished(reply))

    def _commit_finished(self, reply: QNetworkReply) -> None:
        if reply is not self._catalog_reply:
            return
        self._catalog_reply = None
        try:
            if self._status(reply) != 200 or not self._valid_final_url(reply.url()):
                raise ValueError(self._http_detail(self._status(reply)))
            payload = self._read_limited(reply, MAX_CATALOG_BYTES)
            data = json.loads(payload.decode("utf-8"))
            commit = data.get("sha")
            tree = data.get("commit", {}).get("tree", {}).get("sha")
            if (
                not isinstance(commit, str)
                or not GIT_SHA_PATTERN.fullmatch(commit)
                or not isinstance(tree, str)
                or not GIT_SHA_PATTERN.fullmatch(tree)
            ):
                raise ValueError("invalid GitHub commit metadata")
            self._fallback_commit = commit
        except (ValueError, UnicodeError, json.JSONDecodeError) as error:
            reply.deleteLater()
            self._catalog_failure(str(error))
            return
        reply.deleteLater()
        tree_reply = self.network.get(self._request(TREE_URL_PREFIX + tree))
        self._catalog_reply = tree_reply
        tree_reply.finished.connect(lambda: self._tree_finished(tree_reply))

    def _tree_finished(self, reply: QNetworkReply) -> None:
        if reply is not self._catalog_reply:
            return
        self._catalog_reply = None
        try:
            if self._status(reply) != 200 or not self._valid_final_url(reply.url()):
                raise ValueError(self._http_detail(self._status(reply)))
            snapshot = parse_github_tree(
                self._read_limited(reply, MAX_CATALOG_BYTES),
                commit_revision=self._fallback_commit,
            )
            self.cache.save(snapshot)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as error:
            reply.deleteLater()
            self._catalog_failure(str(error))
            return
        reply.deleteLater()
        self.catalog_loaded.emit(snapshot)

    def _catalog_failure(self, detail: str) -> None:
        cached = self.cache.load()
        if cached:
            self.catalog_loaded.emit(cached)
            self.catalog_failed.emit(detail, True)
        else:
            self.catalog_failed.emit(detail, False)

    @staticmethod
    def _http_detail(status: int) -> str:
        if status == 403:
            return "GitHub rate limit or access restriction"
        if status:
            return f"HTTP {status}"
        return "Network request failed"

    def install(self, entry: DictionaryCatalogEntry) -> None:
        if entry.code in self._downloads or entry.code in self._pending:
            self.download_finished.emit(
                entry.code,
                DictionaryOperationResult(
                    False, entry.code, DictionaryError.BUSY, "download already active"
                ),
            )
            return
        if len(self._downloads) >= self.MAX_CONCURRENT_DOWNLOADS:
            self._pending[entry.code] = entry
            return
        self._start_install(entry)

    def _start_install(self, entry: DictionaryCatalogEntry) -> bool:
        if not DictionaryStore.is_safe_filename(entry.filename):
            self.download_finished.emit(
                entry.code,
                DictionaryOperationResult(
                    False, entry.code, DictionaryError.INVALID_FILE
                ),
            )
            return False

        try:
            self.destination.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            self.download_finished.emit(
                entry.code,
                DictionaryOperationResult(
                    False,
                    entry.code,
                    self._storage_error(str(error)),
                    str(error),
                ),
            )
            return False
        target = self.destination / entry.filename
        if target.is_symlink() or target.exists():
            self.download_finished.emit(
                entry.code,
                DictionaryOperationResult(
                    False,
                    entry.code,
                    DictionaryError.CONFLICT,
                    "dictionary is already installed",
                ),
            )
            return False
        output = QSaveFile(str(target))
        if not output.open(QIODevice.OpenModeFlag.WriteOnly):
            self.download_finished.emit(
                entry.code,
                DictionaryOperationResult(
                    False,
                    entry.code,
                    self._storage_error(output.errorString()),
                    output.errorString(),
                ),
            )
            return False
        reply = self.network.get(self._request(entry.download_url))
        git_hash = sha1()
        git_hash.update(f"blob {entry.size}\0".encode("ascii"))
        transfer = _Download(entry, reply, output, sha256(), git_hash)
        self._downloads[entry.code] = transfer
        reply.readyRead.connect(lambda: self._consume(entry.code))
        reply.downloadProgress.connect(
            lambda received, total: self.download_progress.emit(
                entry.code, int(received), int(total or entry.size)
            )
        )
        reply.finished.connect(lambda: self._download_done(entry.code))
        return True

    def _consume(self, code: str) -> None:
        transfer = self._downloads.get(code)
        if transfer is None or transfer.failed is not None:
            return
        while transfer.reply.bytesAvailable():
            chunk = bytes(transfer.reply.read(256 * 1024))
            if not chunk:
                break
            transfer.received += len(chunk)
            if transfer.received > transfer.entry.size:
                transfer.failed = DictionaryOperationResult(
                    False, code, DictionaryError.SIZE, "download exceeds manifest size"
                )
                transfer.reply.abort()
                return
            if transfer.output.write(chunk) != len(chunk):
                transfer.failed = DictionaryOperationResult(
                    False,
                    code,
                    self._storage_error(transfer.output.errorString()),
                    transfer.output.errorString(),
                )
                transfer.reply.abort()
                return
            transfer.sha256_hash.update(chunk)
            transfer.git_hash.update(chunk)

    def _download_done(self, code: str) -> None:
        transfer = self._downloads.get(code)
        if transfer is None:
            return
        self._consume(code)
        result = transfer.failed
        status = self._status(transfer.reply)
        if result is None and transfer.cancelled:
            result = DictionaryOperationResult(
                False, code, DictionaryError.CANCELLED, "download cancelled"
            )
        if result is None and (
            transfer.reply.error() != QNetworkReply.NetworkError.NoError
            or status != 200
        ):
            if transfer.reply.error() == QNetworkReply.NetworkError.TimeoutError:
                error = DictionaryError.TIMEOUT
            elif status == 403:
                error = DictionaryError.RATE_LIMIT
            elif status:
                error = DictionaryError.HTTP
            else:
                error = DictionaryError.NETWORK
            result = DictionaryOperationResult(
                False, code, error, self._http_detail(status)
            )
        if result is None and not self._valid_final_url(
            transfer.reply.url(), expected_filename=transfer.entry.filename
        ):
            result = DictionaryOperationResult(
                False, code, DictionaryError.REDIRECT, "unexpected download URL"
            )
        if result is None and transfer.received != transfer.entry.size:
            result = DictionaryOperationResult(
                False, code, DictionaryError.SIZE, "download size does not match catalog"
            )
        if (
            result is None
            and transfer.entry.sha256
            and transfer.sha256_hash.hexdigest() != transfer.entry.sha256
        ):
            result = DictionaryOperationResult(
                False, code, DictionaryError.HASH, "SHA-256 does not match catalog"
            )
        if (
            result is None
            and transfer.entry.git_sha
            and transfer.git_hash.hexdigest() != transfer.entry.git_sha
        ):
            result = DictionaryOperationResult(
                False, code, DictionaryError.HASH, "Git blob hash does not match catalog"
            )
        if result is None and not transfer.output.commit():
            result = DictionaryOperationResult(
                False,
                code,
                self._storage_error(transfer.output.errorString()),
                transfer.output.errorString(),
            )
        elif result is not None:
            transfer.output.cancelWriting()
        if result is None:
            result = DictionaryOperationResult(True, code)
        transfer.reply.deleteLater()
        self._downloads.pop(code, None)
        self.download_finished.emit(code, result)
        self._start_pending()

    def _start_pending(self) -> None:
        if self._closing:
            return
        while self._pending and len(self._downloads) < self.MAX_CONCURRENT_DOWNLOADS:
            code = next(iter(self._pending))
            entry = self._pending.pop(code)
            self._start_install(entry)

    def cancel(self, code: str) -> None:
        pending = self._pending.pop(code, None)
        if pending is not None:
            self.download_finished.emit(
                code,
                DictionaryOperationResult(
                    False, code, DictionaryError.CANCELLED, "download cancelled"
                ),
            )
            return
        transfer = self._downloads.get(code)
        if transfer is not None:
            transfer.cancelled = True
            transfer.reply.abort()

    @staticmethod
    def _storage_error(detail: str) -> DictionaryError:
        normalized = (detail or "").casefold()
        if "no space" in normalized or "disk full" in normalized:
            return DictionaryError.DISK_FULL
        return DictionaryError.PERMISSION

    def close(self) -> None:
        self._closing = True
        if self._catalog_reply is not None:
            reply = self._catalog_reply
            self._catalog_reply = None
            reply.abort()
        for code in tuple(self._downloads):
            self.cancel(code)
        for code in tuple(self._pending):
            self.cancel(code)
