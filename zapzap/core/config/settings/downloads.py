"""Download behavior settings domain."""

from __future__ import annotations

import logging

from zapzap.core.config.settings.base import BaseSettings
from zapzap.core.config.settings_manager import SettingsManager


logger = logging.getLogger(__name__)


class DownloadBehavior:
    """Stable persisted identifiers for download handling."""

    DIALOG = "dialog"
    AUTOMATIC = "automatic"
    ASK_EVERY_TIME = "ask_every_time"

    VALUES = {DIALOG, AUTOMATIC, ASK_EVERY_TIME}


class MultipleDownloadPermission:
    """Stable permission values for repeated WhatsApp downloads."""

    ASK = "ask"
    ALLOW = "allow"
    BLOCK = "block"

    VALUES = {ASK, ALLOW, BLOCK}


class DownloadSettings(BaseSettings):
    """Semantic access to download behavior preferences."""

    _BEHAVIOR = ("downloads/behavior", DownloadBehavior.DIALOG)
    _AUTO_OPEN_MEDIA_LEGACY = ("downloads/auto_open_media", False)
    _AUTO_OPEN_PDF = ("downloads/auto_open_pdf", False)
    _AUTO_OPEN_IMAGES = ("downloads/auto_open_images", False)
    _MULTIPLE_DOWNLOAD_PERMISSION = (
        "downloads/whatsapp_multiple_download_permission",
        MultipleDownloadPermission.ASK,
    )

    @property
    def behavior(self) -> str:
        raw_value = self._get(self._BEHAVIOR)
        value = (
            raw_value
            if isinstance(raw_value, str)
            and raw_value in DownloadBehavior.VALUES
            else DownloadBehavior.DIALOG
        )
        if value != raw_value:
            logger.warning(
                "Invalid stored download behavior; replacing it with dialog"
            )
            self._set_str(self._BEHAVIOR, value)
        return value

    @behavior.setter
    def behavior(self, value: str) -> None:
        normalized = (
            value if value in DownloadBehavior.VALUES
            else DownloadBehavior.DIALOG
        )
        self._set_str(self._BEHAVIOR, normalized)

    def _migrate_legacy_auto_open(self) -> None:
        legacy_key, _default = self._AUTO_OPEN_MEDIA_LEGACY
        if not SettingsManager.contains(legacy_key):
            return

        legacy_value = self._get_bool(self._AUTO_OPEN_MEDIA_LEGACY)
        pdf_key, _ = self._AUTO_OPEN_PDF
        images_key, _ = self._AUTO_OPEN_IMAGES

        if not SettingsManager.contains(pdf_key):
            self._set_bool(self._AUTO_OPEN_PDF, legacy_value)
        if not SettingsManager.contains(images_key):
            self._set_bool(self._AUTO_OPEN_IMAGES, legacy_value)

        SettingsManager.remove(legacy_key)

    @property
    def auto_open_pdf(self) -> bool:
        self._migrate_legacy_auto_open()
        return self._get_bool(self._AUTO_OPEN_PDF)

    @auto_open_pdf.setter
    def auto_open_pdf(self, value: bool) -> None:
        self._set_bool(self._AUTO_OPEN_PDF, value)

    @property
    def auto_open_images(self) -> bool:
        self._migrate_legacy_auto_open()
        return self._get_bool(self._AUTO_OPEN_IMAGES)

    @auto_open_images.setter
    def auto_open_images(self, value: bool) -> None:
        self._set_bool(self._AUTO_OPEN_IMAGES, value)

    @property
    def auto_open_media(self) -> bool:
        """Compatibility view used by older callers."""
        return self.auto_open_pdf and self.auto_open_images

    @auto_open_media.setter
    def auto_open_media(self, value: bool) -> None:
        self.auto_open_pdf = value
        self.auto_open_images = value

    @property
    def multiple_download_permission(self) -> str:
        raw_value = self._get_str(self._MULTIPLE_DOWNLOAD_PERMISSION)
        if raw_value in MultipleDownloadPermission.VALUES:
            return raw_value

        self._set_str(
            self._MULTIPLE_DOWNLOAD_PERMISSION,
            MultipleDownloadPermission.ASK,
        )
        return MultipleDownloadPermission.ASK

    @multiple_download_permission.setter
    def multiple_download_permission(self, permission: str) -> None:
        normalized = (
            permission
            if permission in MultipleDownloadPermission.VALUES
            else MultipleDownloadPermission.ASK
        )
        self._set_str(self._MULTIPLE_DOWNLOAD_PERMISSION, normalized)

    def clear_multiple_download_permission(self) -> None:
        self.multiple_download_permission = MultipleDownloadPermission.ASK
