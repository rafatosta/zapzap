"""One-shot retrieval of the local account avatar from WhatsApp Web."""

import base64
import binascii
from dataclasses import dataclass

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QImage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from zapzap.assets.icons.user_icon import UserIcon


@dataclass(frozen=True)
class ProfileSyncResult:
    """Validated avatar data returned by the page."""

    photo_data: str


class ProfileSyncError(ValueError):
    """Raised when the page does not return a usable profile avatar."""


class ProfileSyncService:
    """Read the avatar once without retaining a page or running a timer."""

    SCRIPT = """
(() => {
    const image = document.querySelector(
        'header[data-testid="chatlist-header"] button img'
    );
    return image && image.src ? {avatar: image.src} : null;
})()
"""

    @classmethod
    def capture(cls, page, callback):
        """Read the avatar URL once, then download and normalize its bytes."""
        if page is None or not hasattr(page, "runJavaScript"):
            callback(None, ProfileSyncError("WhatsApp Web is unavailable."))
            return

        def handle_payload(payload):
            try:
                if not isinstance(payload, dict):
                    raise ProfileSyncError(
                        "The WhatsApp page returned invalid avatar data."
                    )
                cls._download_avatar(page, payload.get("avatar"), callback)
            except (TypeError, ValueError) as error:
                callback(None, ProfileSyncError(str(error)))

        try:
            page.runJavaScript(cls.SCRIPT, handle_payload)
        except Exception as error:
            callback(None, ProfileSyncError(str(error)))

    @classmethod
    def _download_avatar(cls, page, value, callback):
        if not isinstance(value, str) or not value:
            callback(None, ProfileSyncError("No profile photo is available."))
            return
        if value.startswith("data:image/"):
            try:
                callback(ProfileSyncResult(cls._photo_from_url(value)), None)
            except (TypeError, ValueError, binascii.Error) as error:
                callback(None, ProfileSyncError(str(error)))
            return

        url = QUrl(value)
        if not url.isValid() or url.scheme() not in {"http", "https"}:
            callback(None, ProfileSyncError("The profile photo URL is invalid."))
            return

        manager = QNetworkAccessManager(page)
        reply = manager.get(QNetworkRequest(url))

        def finish():
            try:
                if reply.error() != reply.NetworkError.NoError:
                    raise ProfileSyncError(
                        "The profile photo could not be downloaded."
                    )
                image = QImage()
                if not image.loadFromData(bytes(reply.readAll())):
                    raise ProfileSyncError("The profile photo is invalid.")
                callback(
                    ProfileSyncResult(UserIcon.photo_from_image(image)),
                    None,
                )
            except (TypeError, ValueError, binascii.Error) as error:
                callback(None, ProfileSyncError(str(error)))
            finally:
                reply.deleteLater()
                manager.deleteLater()

        reply.finished.connect(finish)

    @classmethod
    def result_from_payload(cls, payload) -> ProfileSyncResult:
        """Normalize a data URL payload for unit tests and local callers."""
        if not isinstance(payload, dict):
            raise ProfileSyncError("The WhatsApp page returned invalid avatar data.")
        return ProfileSyncResult(cls._photo_from_url(payload.get("avatar")))

    @staticmethod
    def _photo_from_url(value):
        if not isinstance(value, str) or not value.startswith("data:image/"):
            raise ProfileSyncError("The profile photo is not readable.")
        try:
            header, encoded = value.split(",", 1)
            if ";base64" not in header:
                raise ValueError("The profile photo is not base64 encoded.")
            image_bytes = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ProfileSyncError("The profile photo could not be decoded.") from error

        image = QImage()
        if not image.loadFromData(image_bytes):
            raise ProfileSyncError("The profile photo could not be read.")
        return UserIcon.photo_from_image(image)
