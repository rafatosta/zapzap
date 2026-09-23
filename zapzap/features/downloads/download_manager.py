from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

from gettext import gettext as _

from PyQt6.QtCore import QMimeDatabase, QStandardPaths, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog

from zapzap.core.config.settings.downloads import (
    DownloadBehavior,
    DownloadSettings,
    MultipleDownloadPermission,
)
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.downloads.download_events import download_events
from zapzap.features.downloads.download_naming_service import DownloadNamingService


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    MAX_ACTIVE_DOWNLOADS = 6
    PROGRESS_RING_MIN_ETA_SECONDS = 5.0
    MAX_RECENT_DOWNLOADS = 100
    MAX_SESSION_RECORDS = 100

    _floating_cards = []
    _active_downloads = []
    _queued_downloads = []
    _download_meta = {}
    _terminal_records = []
    _has_seen_download_request = False
    _sequence = 0

    _RECENT_DOWNLOADS_KEY = "system/recent_downloads"

    SAFE_AUTO_OPEN_TYPES = {
        "application/pdf": {".pdf"},
        "image/jpeg": {".jpg", ".jpeg", ".jpe"},
        "image/png": {".png"},
        "image/gif": {".gif"},
        "image/webp": {".webp"},
        "image/bmp": {".bmp"},
        "image/tiff": {".tif", ".tiff"},
        "image/x-icon": {".ico"},
        "image/vnd.microsoft.icon": {".ico"},
        "image/avif": {".avif"},
    }

    @staticmethod
    def set_path(new_path):
        path = (
            new_path
            if isinstance(new_path, str) and new_path.strip()
            else DownloadManager.DOWNLOAD_PATH
        )
        SettingsManager.set("system/download_path", path)

    @staticmethod
    def get_path():
        path = SettingsManager.get(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH,
        )
        if not isinstance(path, str) or not path.strip():
            logger.warning(
                "Invalid stored download directory; replacing it with the default"
            )
            path = DownloadManager.DOWNLOAD_PATH
            DownloadManager.set_path(path)
        return path

    @staticmethod
    def restore_path():
        SettingsManager.set(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH,
        )

    @staticmethod
    def on_downloadRequested(
        download: QWebEngineDownloadRequest,
        parent=None,
    ):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
        from zapzap.features.downloads.ui.download_dialog import DownloadDialog

        if (
            download.state()
            != QWebEngineDownloadRequest.DownloadState.DownloadRequested
        ):
            return

        if not DownloadManager._set_initial_download_parameters(
            download,
            parent,
        ):
            return

        DownloadManager._register_download(download)

        if not DownloadManager._authorize_repeated_download(parent):
            DownloadManager._cancel_download(download, "blocked")
            return

        settings = DownloadSettings()
        behavior = settings.behavior
        direct_mode = behavior != DownloadBehavior.DIALOG

        if behavior == DownloadBehavior.AUTOMATIC:
            DownloadManager.start_or_queue(download)
            if direct_mode:
                DownloadManager._emit_direct_activity(download)
            return

        if behavior == DownloadBehavior.ASK_EVERY_TIME:
            if DownloadManager._choose_download_target(download, parent):
                DownloadManager.start_or_queue(download)
                if direct_mode:
                    DownloadManager._emit_direct_activity(download)
            else:
                DownloadManager._discard_unstarted_download(download)
            return

        dialog = DownloadDialog(download, parent)
        DownloadManager._floating_cards.append(dialog)

        try:
            dialog.exec()
        finally:
            if dialog in DownloadManager._floating_cards:
                DownloadManager._floating_cards.remove(dialog)

            try:
                state = download.state()
            except RuntimeError:
                state = None

            if (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadRequested
                and download not in DownloadManager._queued_downloads
            ):
                DownloadManager._discard_unstarted_download(download)

    @staticmethod
    def _register_download(download):
        key = DownloadManager._download_key(download)
        if download not in DownloadManager._active_downloads:
            DownloadManager._active_downloads.append(download)

        DownloadManager._sequence += 1
        DownloadManager._download_meta[key] = {
            "sequence": DownloadManager._sequence,
            "status": "requested",
            "open_on_complete": False,
            "terminal_override": None,
            "suppress_terminal": False,
            "started_at": None,
            "speed_last_at": None,
            "speed_last_received": None,
            "speed_bps": None,
        }

        download.stateChanged.connect(
            lambda state, item=download: DownloadManager._handle_state(
                item,
                state,
            )
        )
        download.receivedBytesChanged.connect(
            download_events.progress_changed.emit
        )
        download.totalBytesChanged.connect(
            download_events.progress_changed.emit
        )
        download.isPausedChanged.connect(
            download_events.items_changed.emit
        )
        download_events.items_changed.emit()

    @staticmethod
    def _authorize_repeated_download(parent) -> bool:
        from zapzap.features.downloads.ui.multiple_download_dialog import (
            MultipleDownloadDecision,
            MultipleDownloadDialog,
        )

        # Qt does not expose whether downloadRequested came from a user gesture.
        # Therefore only the first request in an application session is
        # implicitly allowed. Every later request requires the persisted
        # WhatsApp-wide permission or an explicit one-time decision.
        if not DownloadManager._has_seen_download_request:
            DownloadManager._has_seen_download_request = True
            return True

        settings = DownloadSettings()
        permission = settings.multiple_download_permission

        if permission == MultipleDownloadPermission.ALLOW:
            return True
        if permission == MultipleDownloadPermission.BLOCK:
            return False

        decision = MultipleDownloadDialog.ask(parent)
        if decision == MultipleDownloadDecision.ALWAYS_ALLOW:
            settings.multiple_download_permission = (
                MultipleDownloadPermission.ALLOW
            )
            return True

        if decision == MultipleDownloadDecision.ALLOW_ONCE:
            return True

        settings.multiple_download_permission = MultipleDownloadPermission.BLOCK
        return False

    @staticmethod
    def start_or_queue(download, open_on_complete=False):
        meta = DownloadManager._meta(download)
        if meta is None:
            return "unavailable"

        if open_on_complete:
            meta["open_on_complete"] = True

        if (
            DownloadManager._active_download_count()
            >= DownloadManager.MAX_ACTIVE_DOWNLOADS
        ):
            if download not in DownloadManager._queued_downloads:
                DownloadManager._queued_downloads.append(download)
            meta["status"] = "queued"
            download_events.items_changed.emit()
            download_events.progress_changed.emit()
            return "queued"

        return DownloadManager._begin_download(download)

    @staticmethod
    def _begin_download(download):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

        meta = DownloadManager._meta(download)
        if meta is None:
            return "unavailable"

        try:
            state = download.state()
            if meta.get("started_at") is None:
                meta["started_at"] = time.monotonic()

            if (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadRequested
            ):
                download.accept()
            elif (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
            ):
                download.resume()
            elif (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadInProgress
                and download.isPaused()
            ):
                download.resume()
            elif (
                state
                != QWebEngineDownloadRequest.DownloadState.DownloadInProgress
            ):
                return "unavailable"
        except RuntimeError:
            logger.exception("Download could not be started or resumed")
            DownloadManager._cancel_download(download, "cancelled")
            return "unavailable"

        if download in DownloadManager._queued_downloads:
            DownloadManager._queued_downloads.remove(download)
        meta["status"] = "active"
        meta["speed_last_at"] = time.monotonic()
        meta["speed_last_received"] = DownloadManager._safe_int(
            download,
            "receivedBytes",
            0,
        )
        meta["speed_bps"] = None
        download_events.items_changed.emit()
        download_events.progress_changed.emit()
        return "started"

    @staticmethod
    def pause_download(key):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

        download = DownloadManager._find_download(key)
        if download is None:
            return False

        try:
            if (
                download.state()
                != QWebEngineDownloadRequest.DownloadState.DownloadInProgress
                or download.isPaused()
            ):
                return False
            download.pause()
        except RuntimeError:
            return False

        meta = DownloadManager._meta(download)
        if meta is not None:
            meta["status"] = "paused"
        download_events.items_changed.emit()
        download_events.progress_changed.emit()
        DownloadManager._drain_queue()
        return True

    @staticmethod
    def resume_download(key):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

        download = DownloadManager._find_download(key)
        if download is None:
            return False

        try:
            state = download.state()
            if (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadInProgress
                and download.isPaused()
            ):
                result = DownloadManager.start_or_queue(download)
                return result in {"started", "queued"}

            if (
                state
                != QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
            ):
                return False
        except RuntimeError:
            return False

        result = DownloadManager.start_or_queue(download)
        return result in {"started", "queued"}

    @staticmethod
    def cancel_download(key):
        download = DownloadManager._find_download(key)
        if download is None:
            return False
        DownloadManager._cancel_download(download, "cancelled")
        return True

    @staticmethod
    def _discard_unstarted_download(download):
        """Cancel a request that never started without creating history."""
        meta = DownloadManager._meta(download)
        if meta is not None:
            meta["suppress_terminal"] = True
        try:
            download.cancel()
        except RuntimeError:
            DownloadManager._release_download(download)
        return False

    @staticmethod
    def _cancel_download(download, status="cancelled"):
        meta = DownloadManager._meta(download)
        if meta is not None:
            meta["terminal_override"] = status

        try:
            download.cancel()
        except RuntimeError:
            logger.exception("Download could not be cancelled")
            DownloadManager._record_terminal(download, status)
            DownloadManager._release_download(download)
        return False

    @staticmethod
    def _handle_state(download, state):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

        meta = DownloadManager._meta(download)
        if meta is None:
            return

        if state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
            try:
                meta["status"] = (
                    "paused" if download.isPaused() else "active"
                )
            except RuntimeError:
                meta["status"] = "active"
            download_events.items_changed.emit()
            download_events.progress_changed.emit()
            return

        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            path = DownloadManager._record_completed_download(download)
            if path:
                DownloadManager._record_terminal(download, "completed")
                settings = DownloadSettings()
                auto_open_kind = DownloadManager.auto_open_kind(
                    DownloadManager._safe_mime_type(download),
                    os.path.basename(path),
                    path,
                )
                should_open = meta.get("open_on_complete", False)
                should_open = should_open or (
                    auto_open_kind == "pdf" and settings.auto_open_pdf
                )
                should_open = should_open or (
                    auto_open_kind == "image" and settings.auto_open_images
                )
                if should_open:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(path))

            DownloadManager._release_download(download)
            if path:
                download_events.completed.emit(path)
            DownloadManager._drain_queue()
            return

        if state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            if meta.get("suppress_terminal"):
                DownloadManager._release_download(download)
                DownloadManager._drain_queue()
                return

            status = meta.get("terminal_override") or "cancelled"
            DownloadManager._record_terminal(download, status)
            DownloadManager._release_download(download)
            DownloadManager._drain_queue()
            return

        if state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            try:
                resumable = not download.isFinished()
            except RuntimeError:
                resumable = False

            if resumable:
                meta["status"] = "interrupted"
                if download in DownloadManager._queued_downloads:
                    DownloadManager._queued_downloads.remove(download)
                download_events.items_changed.emit()
                download_events.progress_changed.emit()
                DownloadManager._drain_queue()
                return

            DownloadManager._record_terminal(download, "interrupted")
            DownloadManager._release_download(download)
            DownloadManager._drain_queue()

    @staticmethod
    def _drain_queue():
        for download in tuple(DownloadManager._queued_downloads):
            if DownloadManager._meta(download) is None:
                DownloadManager._queued_downloads.remove(download)
                continue

            if (
                DownloadManager._active_download_count()
                >= DownloadManager.MAX_ACTIVE_DOWNLOADS
            ):
                break

            DownloadManager._begin_download(download)

    @staticmethod
    def _active_download_count():
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

        count = 0
        for download in tuple(DownloadManager._active_downloads):
            try:
                if (
                    download.state()
                    == QWebEngineDownloadRequest.DownloadState.DownloadInProgress
                    and not download.isPaused()
                ):
                    count += 1
            except RuntimeError:
                continue
        return count

    @staticmethod
    def _record_terminal(download, status):
        meta = DownloadManager._meta(download) or {}
        path = DownloadManager._download_path(download)
        try:
            reason = download.interruptReasonString() or ""
        except RuntimeError:
            reason = ""

        DownloadManager._terminal_records.append(
            {
                "key": f"terminal-{time.monotonic_ns()}",
                "path": path,
                "name": os.path.basename(path) if path else _("Download"),
                "status": status,
                "received": DownloadManager._safe_int(
                    download,
                    "receivedBytes",
                    -1,
                ),
                "total": DownloadManager._safe_int(
                    download,
                    "totalBytes",
                    -1,
                ),
                "percent": DownloadManager._percent_for_download(download),
                "reason": reason,
                "resumable": False,
                "live": False,
                "sequence": meta.get("sequence", 0),
                "started_at": meta.get("started_at"),
            },
        )
        DownloadManager._terminal_records.sort(
            key=lambda item: item.get("sequence", 0),
            reverse=True,
        )
        del DownloadManager._terminal_records[
            DownloadManager.MAX_SESSION_RECORDS:
        ]
        download_events.items_changed.emit()

    @staticmethod
    def _release_download(download):
        if download in DownloadManager._queued_downloads:
            DownloadManager._queued_downloads.remove(download)
        if download in DownloadManager._active_downloads:
            DownloadManager._active_downloads.remove(download)

        DownloadManager._download_meta.pop(
            DownloadManager._download_key(download),
            None,
        )
        download_events.items_changed.emit()
        download_events.progress_changed.emit()

    @staticmethod
    def _record_completed_download(download):
        path = DownloadManager._download_path(download)
        if not path:
            return None

        recent = SettingsManager.get(
            DownloadManager._RECENT_DOWNLOADS_KEY,
            [],
        )
        if isinstance(recent, str):
            recent = [recent]
        elif not isinstance(recent, (list, tuple)):
            recent = []

        normalized = os.path.normcase(path)
        recent = [
            item
            for item in recent
            if isinstance(item, str)
            and os.path.normcase(os.path.normpath(item)) != normalized
        ]
        recent.insert(0, path)
        SettingsManager.set(
            DownloadManager._RECENT_DOWNLOADS_KEY,
            recent[:DownloadManager.MAX_RECENT_DOWNLOADS],
        )
        return path

    @staticmethod
    def download_items():
        session_items = []
        live_paths = set()

        for download in tuple(DownloadManager._active_downloads):
            item = DownloadManager._snapshot(download)
            if item is None:
                continue
            session_items.append(item)
            if item["path"]:
                live_paths.add(os.path.normcase(item["path"]))

        session_items.extend(
            dict(record) for record in DownloadManager._terminal_records
        )
        session_items.sort(
            key=lambda item: item.get("sequence", 0),
            reverse=True,
        )

        items = list(session_items)
        terminal_paths = {
            os.path.normcase(item["path"])
            for item in DownloadManager._terminal_records
            if item.get("path")
        }
        for index, path in enumerate(DownloadManager.recent_downloads()):
            normalized = os.path.normcase(path)
            if normalized in live_paths or normalized in terminal_paths:
                continue
            items.append(
                {
                    "key": f"completed-{index}-{path}",
                    "path": path,
                    "name": os.path.basename(path),
                    "status": "completed",
                    "received": -1,
                    "total": -1,
                    "percent": 100,
                    "reason": "",
                    "resumable": False,
                    "live": False,
                    "sequence": -(index + 1),
                    "started_at": None,
                }
            )

        return items

    @staticmethod
    def _snapshot(download):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

        meta = DownloadManager._meta(download)
        if meta is None:
            return None

        path = DownloadManager._download_path(download)
        received = DownloadManager._safe_int(download, "receivedBytes", -1)
        total = DownloadManager._safe_int(download, "totalBytes", -1)
        percent = DownloadManager._percent(received, total)

        status = meta.get("status", "requested")
        resumable = False
        reason = ""

        try:
            state = download.state()
            if download in DownloadManager._queued_downloads:
                status = "queued"
            elif (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadInProgress
            ):
                status = "paused" if download.isPaused() else "active"
            elif (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
            ):
                status = "interrupted"
                resumable = not download.isFinished()
                reason = download.interruptReasonString() or ""
            elif (
                state
                == QWebEngineDownloadRequest.DownloadState.DownloadRequested
            ):
                status = "queued" if download in DownloadManager._queued_downloads else "requested"
        except RuntimeError:
            return None

        speed_bps, eta_seconds = DownloadManager._speed_and_eta(
            meta,
            received,
            total,
            status,
        )

        return {
            "key": DownloadManager._download_key(download),
            "path": path,
            "name": (
                os.path.basename(path)
                if path
                else DownloadManager._safe_file_name(download)
            ),
            "status": status,
            "received": received,
            "total": total,
            "percent": percent,
            "reason": reason,
            "resumable": resumable,
            "live": True,
            "sequence": meta.get("sequence", 0),
            "started_at": meta.get("started_at"),
            "speed_bps": speed_bps,
            "eta_seconds": eta_seconds,
        }

    @staticmethod
    def _speed_and_eta(meta, received, total, status):
        """Return smoothed transfer speed and estimated seconds remaining."""
        if status != "active" or received < 0:
            return None, None

        now = time.monotonic()
        last_at = meta.get("speed_last_at")
        last_received = meta.get("speed_last_received")
        speed = meta.get("speed_bps")

        if (
            last_at is None
            or last_received is None
            or received < last_received
        ):
            meta["speed_last_at"] = now
            meta["speed_last_received"] = received
            return speed if speed and speed > 0 else None, None

        elapsed = now - last_at
        if elapsed >= 0.25:
            transferred = max(0, received - last_received)
            instant_speed = transferred / elapsed

            if instant_speed > 0:
                if speed is None or speed <= 0:
                    speed = instant_speed
                else:
                    speed = (speed * 0.65) + (instant_speed * 0.35)
                meta["speed_bps"] = speed

            meta["speed_last_at"] = now
            meta["speed_last_received"] = received

        if speed is None or speed <= 0:
            return None, None

        eta_seconds = None
        if total > 0 and received < total:
            eta_seconds = max(0.0, (total - received) / speed)

        return speed, eta_seconds

    @staticmethod
    def item_snapshot(key):
        download = DownloadManager._find_download(key)
        if download is not None:
            return DownloadManager._snapshot(download)

        for record in DownloadManager._terminal_records:
            if record.get("key") == key:
                return dict(record)
        return None

    @staticmethod
    def active_downloads():
        return [
            item["path"]
            for item in DownloadManager.download_items()
            if item.get("live") and item.get("path")
        ]

    @staticmethod
    def progress_summary():
        count = 0
        received_total = 0
        expected_total = 0
        unknown_size = False

        for item in DownloadManager.download_items():
            if not item.get("live"):
                continue
            if item["status"] not in {
                "active",
                "paused",
                "queued",
                "interrupted",
            }:
                continue

            count += 1
            received = item.get("received", -1)
            total = item.get("total", -1)
            if total <= 0 or received < 0:
                unknown_size = True
                continue

            received_total += min(received, total)
            expected_total += total

        if count == 0:
            return 0, None
        if unknown_size or expected_total <= 0:
            return count, None

        percent = round((received_total * 100) / expected_total)
        return count, max(0, min(99, percent))

    @staticmethod
    def progress_indicator():
        """Return active count, weighted progress and whether to show the ring."""
        items = [
            item
            for item in DownloadManager.download_items()
            if item.get("live") and item.get("status") == "active"
        ]
        if not items:
            return 0, None, False

        received_total = 0
        expected_total = 0
        eta_values = []

        for item in items:
            received = item.get("received", -1)
            total = item.get("total", -1)
            if total <= 0 or received < 0:
                return len(items), None, False

            received_total += min(received, total)
            expected_total += total

            eta = item.get("eta_seconds")
            if eta is not None:
                eta_values.append(float(eta))

        percent = round((received_total * 100) / expected_total)
        percent = max(0, min(99, percent))

        show_ring = (
            bool(eta_values)
            and max(eta_values) > DownloadManager.PROGRESS_RING_MIN_ETA_SECONDS
        )
        return len(items), percent, show_ring

    @staticmethod
    def recent_downloads():
        recent = SettingsManager.get(
            DownloadManager._RECENT_DOWNLOADS_KEY,
            [],
        )
        if isinstance(recent, str):
            recent = [recent]
        elif not isinstance(recent, (list, tuple)):
            recent = []

        valid = [
            os.path.normpath(item)
            for item in recent
            if isinstance(item, str) and os.path.isfile(item)
        ][:DownloadManager.MAX_RECENT_DOWNLOADS]

        if list(recent) != valid:
            SettingsManager.set(
                DownloadManager._RECENT_DOWNLOADS_KEY,
                valid,
            )
        return valid

    @staticmethod
    def remove_history_item(key, path=""):
        """Remove one finished item from ZapZap history, never from disk."""
        for item in DownloadManager._active_downloads:
            if DownloadManager._download_key(item) == key:
                return False

        before = len(DownloadManager._terminal_records)
        DownloadManager._terminal_records = [
            record
            for record in DownloadManager._terminal_records
            if record.get("key") != key
        ]
        removed = len(DownloadManager._terminal_records) != before

        if path:
            normalized = os.path.normcase(os.path.normpath(path))
            recent = SettingsManager.get(
                DownloadManager._RECENT_DOWNLOADS_KEY,
                [],
            )
            if isinstance(recent, str):
                recent = [recent]
            elif not isinstance(recent, (list, tuple)):
                recent = []

            filtered = [
                item
                for item in recent
                if not (
                    isinstance(item, str)
                    and os.path.normcase(os.path.normpath(item)) == normalized
                )
            ]
            if list(recent) != filtered:
                SettingsManager.set(
                    DownloadManager._RECENT_DOWNLOADS_KEY,
                    filtered,
                )
                removed = True

        if removed:
            download_events.items_changed.emit()
        return removed

    @staticmethod
    def clear_recent_downloads():
        SettingsManager.set(DownloadManager._RECENT_DOWNLOADS_KEY, [])
        DownloadManager._terminal_records.clear()
        download_events.items_changed.emit()

    @staticmethod
    def auto_open_kind(
        mime_type: str,
        file_name: str,
        path: str | None = None,
    ) -> str | None:
        """Return pdf/image only for verified safe automatic-open content."""
        if not path or not os.path.isfile(path):
            return None

        try:
            detected = QMimeDatabase().mimeTypeForFile(
                path,
                QMimeDatabase.MatchMode.MatchContent,
            ).name()
        except Exception:
            logger.exception("Failed to inspect downloaded file MIME type")
            return None

        detected = (detected or "").split(";", 1)[0].strip().lower()
        allowed_extensions = DownloadManager.SAFE_AUTO_OPEN_TYPES.get(detected)
        if not allowed_extensions:
            return None

        extension = os.path.splitext(file_name or path)[1].lower()
        if extension not in allowed_extensions:
            return None

        # A conflicting non-generic server MIME is suspicious. Empty/generic
        # values are tolerated because content sniffing above is authoritative.
        reported = (mime_type or "").split(";", 1)[0].strip().lower()
        generic = {
            "",
            "application/octet-stream",
            "binary/octet-stream",
            "application/force-download",
            "application/download",
            "application/unknown",
        }
        if reported not in generic and reported != detected:
            return None

        return "pdf" if detected == "application/pdf" else "image"

    @staticmethod
    def supports_auto_open(
        mime_type: str,
        file_name: str,
        path: str | None = None,
    ) -> bool:
        return DownloadManager.auto_open_kind(
            mime_type,
            file_name,
            path,
        ) is not None

    @staticmethod
    def set_download_target(
        download,
        directory: str,
        file_name: str,
        mime_type: str | None = None,
        url: str | None = None,
    ) -> tuple[str, str]:
        """Apply a canonical, filename-sanitized target to a download."""
        if mime_type is None:
            mime_type = DownloadManager._safe_mime_type(download)
        if url is None:
            try:
                url = download.url().toString()
            except RuntimeError:
                url = ""

        normalized_name = DownloadNamingService.normalized_file_name(
            file_name,
            mime_type or "",
            url or "",
        )
        safe_directory, safe_name = (
            DownloadNamingService.safe_download_target(
                directory,
                normalized_name,
            )
        )
        download.setDownloadDirectory(safe_directory)
        try:
            current_name = download.downloadFileName()
        except RuntimeError:
            current_name = ""
        if current_name != safe_name:
            download.setDownloadFileName(safe_name)
        return safe_directory, safe_name

    @staticmethod
    def _emit_direct_activity(download):
        path = DownloadManager._download_path(download)
        if path:
            download_events.started.emit(path)

    @staticmethod
    def _download_key(download):
        return id(download)

    @staticmethod
    def _meta(download):
        return DownloadManager._download_meta.get(
            DownloadManager._download_key(download)
        )

    @staticmethod
    def _find_download(key):
        for download in tuple(DownloadManager._active_downloads):
            if DownloadManager._download_key(download) == key:
                return download
        return None

    @staticmethod
    def _download_path(download):
        try:
            directory = download.downloadDirectory()
            file_name = download.downloadFileName()
        except RuntimeError:
            return ""
        if not directory or not file_name:
            return ""

        try:
            safe_directory, safe_name = (
                DownloadNamingService.safe_download_target(
                    directory,
                    file_name,
                )
            )
        except ValueError:
            logger.warning("Rejected download path outside its target directory")
            return ""

        return os.path.join(safe_directory, safe_name)

    @staticmethod
    def _safe_file_name(download):
        try:
            return (
                download.downloadFileName()
                or download.suggestedFileName()
                or _("Download")
            )
        except RuntimeError:
            return _("Download")

    @staticmethod
    def _safe_mime_type(download) -> str:
        try:
            return download.mimeType() or ""
        except RuntimeError:
            return ""

    @staticmethod
    def _safe_int(download, method_name, fallback):
        try:
            return int(getattr(download, method_name)())
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return fallback

    @staticmethod
    def _percent_for_download(download):
        return DownloadManager._percent(
            DownloadManager._safe_int(download, "receivedBytes", -1),
            DownloadManager._safe_int(download, "totalBytes", -1),
        )

    @staticmethod
    def _percent(received, total):
        if total <= 0 or received < 0:
            return None
        return max(
            0,
            min(100, round((min(received, total) * 100) / total)),
        )

    @staticmethod
    def _session_directory(parent):
        """Return the in-memory directory remembered for this conversation."""
        directory = getattr(parent, "last_download_directory", None)
        return (
            directory
            if isinstance(directory, str) and directory.strip()
            else None
        )

    @staticmethod
    def _set_initial_download_parameters(download, parent=None) -> bool:
        configured_path = (
            DownloadManager._session_directory(parent)
            or DownloadManager.get_path()
        )
        try:
            DownloadManager.set_download_target(
                download,
                configured_path,
                download.downloadFileName() or download.suggestedFileName(),
            )
            return True
        except Exception:
            logger.exception(
                "Failed to apply the configured download target; retrying "
                "with the default directory"
            )

        try:
            DownloadManager.set_download_target(
                download,
                DownloadManager.DOWNLOAD_PATH,
                download.downloadFileName() or download.suggestedFileName(),
            )
            DownloadManager.restore_path()
            return True
        except Exception:
            logger.exception(
                "Failed to apply the default download target; cancelling "
                "the download"
            )

        try:
            download.cancel()
        except Exception:
            logger.exception(
                "Failed to cancel a download with no valid target"
            )
        return False

    @staticmethod
    def _file_dialog_options():
        return (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

    @staticmethod
    def _choose_download_target(download, parent=None) -> bool:
        try:
            directory = download.downloadDirectory()
            file_name = download.downloadFileName()
            mime_type = download.mimeType()
            url = download.url().toString()
        except RuntimeError:
            return False

        suffix = os.path.splitext(file_name)[1].lstrip(".")
        name_filter = f"*.{suffix}" if suffix else "*"

        path, _selected_filter = QFileDialog.getSaveFileName(
            parent,
            _("Save file"),
            os.path.join(directory, file_name),
            name_filter,
            options=DownloadManager._file_dialog_options(),
        )
        if not path:
            return False

        try:
            DownloadManager.set_download_target(
                download,
                os.path.dirname(path),
                os.path.basename(path),
                mime_type,
                url,
            )
        except (RuntimeError, ValueError):
            logger.exception("Rejected unsafe selected download target")
            return False
        return True

    @staticmethod
    def open_folder_dialog(parent):
        directory = DownloadManager.get_path()
        folder_path = QFileDialog.getExistingDirectory(
            parent=parent,
            caption=_("Select folder"),
            directory=directory,
            options=DownloadManager._file_dialog_options(),
        )
        return folder_path or None
