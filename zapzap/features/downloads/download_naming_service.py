import mimetypes
import os
import re
from urllib.parse import unquote


class DownloadNamingService:
    PREFERRED_MIME_EXTENSIONS = {
        "application/pdf": ".pdf",
        "application/x-pdf": ".pdf",
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

    GENERIC_MIME_TYPES = {
        "application/octet-stream",
        "binary/octet-stream",
        "application/force-download",
        "application/download",
        "application/unknown",
    }

    _WINDOWS_RESERVED_NAMES = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
    _INVALID_FILE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]')
    _MAX_FILE_NAME_BYTES = 240

    @staticmethod
    def normalized_file_name(
        file_name: str,
        mime_type: str = "",
        url: str = ""
    ) -> str:
        file_name = DownloadNamingService._fallback_file_name(
            file_name,
            mime_type,
            url,
        )
        file_name = DownloadNamingService.sanitize_file_name(file_name)

        if DownloadNamingService._has_extension(file_name):
            return file_name

        extension = DownloadNamingService.extension_for_mime_type(mime_type)
        if not extension:
            return file_name

        file_name = DownloadNamingService._visible_file_name(file_name)
        return DownloadNamingService.sanitize_file_name(
            f"{file_name}{extension}"
        )

    @staticmethod
    def sanitize_file_name(file_name: str) -> str:
        """Return one safe cross-platform basename with no path semantics."""
        value = str(file_name or "").replace("\\", "/")
        value = value.rsplit("/", 1)[-1]
        value = DownloadNamingService._INVALID_FILE_CHARS.sub("_", value)
        value = value.strip().strip(".")
        value = DownloadNamingService._visible_file_name(value)

        if not value or value in {".", ".."}:
            value = "download"

        stem, extension = os.path.splitext(value)
        reserved_stem = stem.rstrip(" .").upper()
        if reserved_stem in DownloadNamingService._WINDOWS_RESERVED_NAMES:
            stem = f"_{stem.rstrip(' .') or 'download'}"
            value = f"{stem}{extension}"

        if (
            len(value.encode("utf-8"))
            > DownloadNamingService._MAX_FILE_NAME_BYTES
        ):
            stem, extension = os.path.splitext(value)
            extension = DownloadNamingService._truncate_utf8(
                extension,
                32,
            )
            available = max(
                1,
                DownloadNamingService._MAX_FILE_NAME_BYTES
                - len(extension.encode("utf-8")),
            )
            stem = DownloadNamingService._truncate_utf8(stem, available)
            value = f"{stem}{extension}"

        return value or "download"

    @staticmethod
    def _truncate_utf8(value: str, maximum_bytes: int) -> str:
        """Trim text without cutting a Unicode code point."""
        if len(value.encode("utf-8")) <= maximum_bytes:
            return value

        encoded = value.encode("utf-8")[:maximum_bytes]
        return encoded.decode("utf-8", errors="ignore")

    @staticmethod
    def safe_download_target(directory: str, file_name: str) -> tuple[str, str]:
        """Return a canonical directory/basename that cannot escape the folder."""
        if not isinstance(directory, str) or not directory.strip():
            raise ValueError("Download directory is empty")

        safe_name = DownloadNamingService.sanitize_file_name(file_name)
        base = os.path.realpath(os.path.abspath(os.path.expanduser(directory)))
        candidate = os.path.realpath(os.path.join(base, safe_name))

        try:
            inside = os.path.commonpath([base, candidate]) == base
        except ValueError as error:
            raise ValueError("Download target is outside its directory") from error

        if not inside:
            raise ValueError("Download target is outside its directory")

        return base, safe_name

    @staticmethod
    def extension_for_mime_type(mime_type: str) -> str:
        normalized_mime_type = DownloadNamingService._normalized_mime_type(
            mime_type
        )
        if not normalized_mime_type:
            return ""

        preferred_extension = DownloadNamingService.PREFERRED_MIME_EXTENSIONS.get(
            normalized_mime_type
        )
        if preferred_extension:
            return preferred_extension

        if normalized_mime_type in DownloadNamingService.GENERIC_MIME_TYPES:
            return ""

        return mimetypes.guess_extension(normalized_mime_type) or ""

    @staticmethod
    def _fallback_file_name(file_name: str, mime_type: str, url: str) -> str:
        file_name = (file_name or "").strip()
        if file_name:
            return file_name

        url_file_name = DownloadNamingService._file_name_from_url(url)
        if url_file_name:
            return url_file_name

        return "download"

    @staticmethod
    def _file_name_from_url(url: str) -> str:
        path = (url or "").split("?", 1)[0].split("#", 1)[0]
        path = path.rstrip("/")
        file_name = os.path.basename(unquote(path))
        return file_name.strip()

    @staticmethod
    def _visible_file_name(file_name: str) -> str:
        return file_name.lstrip(".") or "download"

    @staticmethod
    def _has_extension(file_name: str) -> bool:
        root, extension = os.path.splitext(file_name)
        return bool(root and extension)

    @staticmethod
    def _normalized_mime_type(mime_type: str) -> str:
        return (mime_type or "").split(";", 1)[0].strip().lower()
