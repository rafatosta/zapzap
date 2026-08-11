"""Non-blocking stable-release checks for official manual packages."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import re
from typing import Optional

from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from zapzap import __version__
from zapzap.core.environment.environment_detector import EnvironmentDetector


logger = logging.getLogger(__name__)

LATEST_STABLE_RELEASE_URL = (
    "https://api.github.com/repos/rafatosta/zapzap/releases/latest"
)
OFFICIAL_REPOSITORY = "rafatosta/zapzap"
OFFICIAL_PROVIDER = "GitHub Actions"
MANUAL_UPDATE_PACKAGING = frozenset(
    {
        "DEB",
        "macOS",
        "Windows x86_64 (exe)",
        "Windows arm64 (exe)",
    }
)
_VERSION_PATTERN = re.compile(r"^[vV]?(\d+(?:\.\d+)*)$")


def parse_version(value: str) -> Optional[tuple[int, ...]]:
    """Parse a stable numeric version, normalizing insignificant zeroes."""

    match = _VERSION_PATTERN.fullmatch(str(value or "").strip())
    if match is None:
        return None
    parts = [int(part) for part in match.group(1).split(".")]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def is_newer_version(current: str, latest: str) -> bool:
    """Return whether both versions are valid and ``latest`` is newer."""

    current_parts = parse_version(current)
    latest_parts = parse_version(latest)
    if current_parts is None or latest_parts is None:
        return False
    width = max(len(current_parts), len(latest_parts))
    return current_parts + (0,) * (width - len(current_parts)) < (
        latest_parts + (0,) * (width - len(latest_parts))
    )


def parse_stable_release(payload: bytes) -> Optional[str]:
    """Extract one stable numeric tag from a GitHub release response."""

    try:
        release = json.loads(bytes(payload).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(release, dict):
        return None
    if release.get("draft") is not False or release.get("prerelease") is not False:
        return None
    tag_name = release.get("tag_name")
    if not isinstance(tag_name, str) or parse_version(tag_name) is None:
        return None
    return tag_name.lstrip("vV")


class UpdatePolicy:
    """Conservative policy for official packages requiring manual downloads."""

    @staticmethod
    def should_check(
        channel: str,
        provider: str,
        repository: str,
        packaging: str,
    ) -> bool:
        return (
            channel == "Official"
            and provider == OFFICIAL_PROVIDER
            and str(repository).casefold() == OFFICIAL_REPOSITORY
            and packaging in MANUAL_UPDATE_PACKAGING
        )

    @classmethod
    def should_check_current_environment(cls) -> bool:
        return cls.should_check(
            EnvironmentDetector.CHANNEL,
            EnvironmentDetector.PROVIDER,
            EnvironmentDetector.BUILD_REPOSITORY,
            EnvironmentDetector.PACKAGING,
        )


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    available: bool


class UpdateState(QObject):
    """Session-only update result shared by independent views."""

    changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._info: Optional[UpdateInfo] = None

    @property
    def info(self) -> Optional[UpdateInfo]:
        return self._info

    def set_info(self, info: UpdateInfo) -> None:
        if info == self._info:
            return
        self._info = info
        self.changed.emit(info)


class UpdateChecker(QObject):
    """Perform at most one asynchronous release request for this instance."""

    completed = pyqtSignal(object)
    TIMEOUT_MS = 5000

    def __init__(self, state: UpdateState, parent=None, network_manager=None):
        super().__init__(parent)
        self._state = state
        self._network_manager = network_manager or QNetworkAccessManager(self)
        self._started = False
        self._reply = None

    def start_once(self) -> bool:
        if self._started:
            return False
        self._started = True

        if not UpdatePolicy.should_check_current_environment():
            logger.debug(
                "update check skipped: channel=%s packaging=%s",
                EnvironmentDetector.CHANNEL,
                EnvironmentDetector.PACKAGING,
            )
            return False

        request = QNetworkRequest(QUrl(LATEST_STABLE_RELEASE_URL))
        request.setTransferTimeout(self.TIMEOUT_MS)
        request.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            f"ZapZap/{__version__}",
        )
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        self._reply = self._network_manager.get(request)
        self._reply.finished.connect(self._handle_reply)
        return True

    def _handle_reply(self) -> None:
        reply = self._reply
        self._reply = None
        if reply is None:
            return

        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                logger.debug("update check failed: %s", reply.errorString())
                self.completed.emit(None)
                return

            status = reply.attribute(
                QNetworkRequest.Attribute.HttpStatusCodeAttribute
            )
            if status != 200:
                logger.debug("update check failed: HTTP status %s", status)
                self.completed.emit(None)
                return

            latest = parse_stable_release(bytes(reply.readAll()))
            if latest is None:
                logger.debug("update check failed: invalid stable release response")
                self.completed.emit(None)
                return

            info = UpdateInfo(
                current_version=__version__,
                latest_version=latest,
                available=is_newer_version(__version__, latest),
            )
            logger.info(
                "update check: current=%s latest=%s available=%s",
                info.current_version,
                info.latest_version,
                info.available,
            )
            self._state.set_info(info)
            self.completed.emit(info)
        finally:
            reply.deleteLater()
