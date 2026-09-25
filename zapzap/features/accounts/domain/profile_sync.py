"""One-shot retrieval of profile data from an authenticated WhatsApp page."""

import base64
import binascii
from dataclasses import dataclass

from PyQt6.QtGui import QImage

from zapzap.assets.icons.user_icon import UserIcon


@dataclass(frozen=True)
class ProfileSyncResult:
    """Validated data returned by the page, kept separate from local fields."""

    name: str | None = None
    photo_data: str | None = None


class ProfileSyncError(ValueError):
    """Raised when the page does not return usable profile data."""


class ProfileSyncService:
    """Capture profile data once without retaining a page or running a timer."""

    SCRIPT = """
(() => {
    const visible = element => {
        if (!element) return false;
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && style.visibility !== 'hidden';
    };
    const profileImage = Array.from(document.querySelectorAll(
        'img[alt*="profile" i], img[aria-label*="profile" i], img[title*="profile" i]'
    )).find(image => visible(image) && image.src);
    const named = Array.from(document.querySelectorAll(
        '[aria-label], [title], [data-testid]'
    )).find(element => {
        const value = element.getAttribute('aria-label') ||
            element.getAttribute('title') || '';
        return visible(element) && value.trim() &&
            !/^(profile photo|settings|menu|search|status)$/i.test(value.trim());
    });
    return {
        name: named ? (named.getAttribute('aria-label') || named.getAttribute('title')).trim() : null,
        avatar: profileImage ? profileImage.src : null
    };
})()
"""

    @classmethod
    def capture(cls, page, callback):
        """Run the script once and deliver a ``ProfileSyncResult`` or error."""
        if page is None or not hasattr(page, "runJavaScript"):
            callback(None, ProfileSyncError("WhatsApp Web is unavailable."))
            return

        def handle_payload(payload):
            try:
                callback(cls.result_from_payload(payload), None)
            except (TypeError, ValueError, binascii.Error) as error:
                callback(None, ProfileSyncError(str(error)))

        try:
            page.runJavaScript(cls.SCRIPT, handle_payload)
        except Exception as error:
            callback(None, ProfileSyncError(str(error)))

    @classmethod
    def result_from_payload(cls, payload) -> ProfileSyncResult:
        if not isinstance(payload, dict):
            raise ProfileSyncError("The WhatsApp page returned invalid data.")

        name = payload.get("name")
        if name is not None and not isinstance(name, str):
            raise ProfileSyncError("The WhatsApp profile name is invalid.")
        name = name.strip() if name else None

        photo_data = cls._photo_from_url(payload.get("avatar"))
        if not name and not photo_data:
            raise ProfileSyncError("No profile data is available.")
        return ProfileSyncResult(name=name, photo_data=photo_data)

    @staticmethod
    def _photo_from_url(value):
        if not value:
            return None
        if not isinstance(value, str) or not value.startswith("data:image/"):
            return None
        try:
            header, encoded = value.split(",", 1)
            if ";base64" not in header:
                raise ValueError("The profile image is not base64 encoded.")
            image_bytes = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ProfileSyncError("The profile image could not be decoded.") from error

        image = QImage()
        if not image.loadFromData(image_bytes):
            raise ProfileSyncError("The profile image could not be read.")
        return UserIcon.photo_from_image(image)