import os
from urllib.parse import unquote


class DownloadNamingService:
    IMAGE_MIME_EXTENSIONS = {
        "image/jpeg": ".jpeg",
        "image/jpg": ".jpeg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
        "image/svg+xml": ".svg",
        "image/tiff": ".tiff",
        "image/x-icon": ".ico",
        "image/vnd.microsoft.icon": ".ico",
    }

    @staticmethod
    def normalized_file_name(
        file_name: str,
        mime_type: str = "",
        url: str = ""
    ) -> str:
        file_name = DownloadNamingService._fallback_file_name(
            file_name,
            mime_type,
            url
        )

        if DownloadNamingService._has_extension(file_name):
            return file_name

        extension = DownloadNamingService.extension_for_mime_type(mime_type)
        if not extension:
            return file_name

        file_name = DownloadNamingService._visible_file_name(file_name)
        return f"{file_name}{extension}"

    @staticmethod
    def extension_for_mime_type(mime_type: str) -> str:
        normalized_mime_type = (
            mime_type or ""
        ).split(";", 1)[0].strip().lower()

        return DownloadNamingService.IMAGE_MIME_EXTENSIONS.get(
            normalized_mime_type,
            ""
        )

    @staticmethod
    def _fallback_file_name(file_name: str, mime_type: str, url: str) -> str:
        file_name = (file_name or "").strip()
        if file_name:
            return file_name

        url_file_name = DownloadNamingService._file_name_from_url(url)
        if url_file_name:
            return url_file_name

        if DownloadNamingService.extension_for_mime_type(mime_type):
            return "image"

        return "download"

    @staticmethod
    def _file_name_from_url(url: str) -> str:
        path = (url or "").split("?", 1)[0].split("#", 1)[0]
        path = path.rstrip("/")
        file_name = os.path.basename(unquote(path))
        return file_name.strip()

    @staticmethod
    def _visible_file_name(file_name: str) -> str:
        return file_name.lstrip(".") or "image"

    @staticmethod
    def _has_extension(file_name: str) -> bool:
        root, extension = os.path.splitext(file_name)
        return bool(root and extension)
