import os
import re
import shutil
import urllib.error
import urllib.request

from PyQt6.QtCore import QStandardPaths

from zapzap.services.SettingsManager import SettingsManager


class CssPreviewService:
    MAX_PREVIEW_DOWNLOAD_SIZE = 5 * 1024 * 1024

    @staticmethod
    def _base_dir():
        return os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            ),
            "customizations",
        )

    @staticmethod
    def _scope_dir(scope: str, account_id=None):
        if scope == "global":
            return os.path.join(CssPreviewService._base_dir(), "global")

        account_key = str(account_id if account_id is not None else "default")
        return os.path.join(CssPreviewService._base_dir(), "accounts", account_key)

    @staticmethod
    def _sanitize_file_name(file_name: str, extension: str):
        base_name = os.path.basename(file_name.strip()) if file_name else ""
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", base_name)

        if not safe_name:
            safe_name = f"custom.{extension}"

        if not safe_name.lower().endswith(f".{extension}"):
            safe_name = f"{safe_name}.{extension}"

        return safe_name

    @staticmethod
    def _available_file_path(assets_dir: str, file_name: str):
        name, ext = os.path.splitext(file_name)
        target_path = os.path.join(assets_dir, file_name)
        counter = 1

        while os.path.exists(target_path):
            target_path = os.path.join(assets_dir, f"{name}_{counter}{ext}")
            counter += 1

        return target_path

    @staticmethod
    def _css_preview_map_key(scope: str, account_id=None):
        if scope == "global":
            return "custom/global/css/preview_map"

        return f"custom/accounts/{account_id}/css/preview_map"

    @staticmethod
    def _css_preview_dir(scope: str, account_id=None):
        preview_dir = os.path.join(
            CssPreviewService._scope_dir(scope, account_id),
            "previews",
            "css",
        )
        os.makedirs(preview_dir, exist_ok=True)
        return preview_dir

    @staticmethod
    def _read_css_preview_map(scope: str, account_id=None):
        value = SettingsManager.get(
            CssPreviewService._css_preview_map_key(scope, account_id),
            {},
        )
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items() if k and v}
        return {}

    @staticmethod
    def _write_css_preview_map(scope: str, mapping, account_id=None):
        cleaned = {str(k): str(v) for k, v in mapping.items() if k and v}
        SettingsManager.set(CssPreviewService._css_preview_map_key(scope, account_id), cleaned)

    @staticmethod
    def _remove_preview_file_if_unreferenced(scope: str, preview_file_name: str, account_id=None):
        mapping = CssPreviewService._read_css_preview_map(scope, account_id)
        if preview_file_name in mapping.values():
            return

        preview_path = os.path.join(CssPreviewService._css_preview_dir(scope, account_id), preview_file_name)
        try:
            if os.path.isfile(preview_path):
                os.remove(preview_path)
        except OSError:
            pass

    @staticmethod
    def get_css_preview_path(file_name: str, scope: str, account_id=None):
        mapping = CssPreviewService._read_css_preview_map(scope, account_id)
        preview_file_name = mapping.get(file_name)
        if not preview_file_name:
            return None

        preview_path = os.path.join(CssPreviewService._css_preview_dir(scope, account_id), preview_file_name)
        if not os.path.isfile(preview_path):
            mapping.pop(file_name, None)
            CssPreviewService._write_css_preview_map(scope, mapping, account_id)
            return None

        return preview_path

    @staticmethod
    def _set_css_preview_file_name(file_name: str, preview_file_name: str, scope: str, account_id=None):
        mapping = CssPreviewService._read_css_preview_map(scope, account_id)
        old_preview_file = mapping.get(file_name)
        mapping[file_name] = preview_file_name
        CssPreviewService._write_css_preview_map(scope, mapping, account_id)

        if old_preview_file and old_preview_file != preview_file_name:
            CssPreviewService._remove_preview_file_if_unreferenced(
                scope,
                old_preview_file,
                account_id,
            )

    @staticmethod
    def set_css_preview_from_file(file_name: str, source_path: str, scope: str, account_id=None):
        preview_dir = CssPreviewService._css_preview_dir(scope, account_id)
        extension = os.path.splitext(source_path)[1].lower().lstrip(".") or "png"
        extension = "png" if extension not in {"png", "jpg", "jpeg", "webp", "gif", "bmp"} else extension
        suggested = f"{os.path.splitext(file_name)[0]}.{extension}"
        safe_name = CssPreviewService._sanitize_file_name(suggested, extension)
        target_path = CssPreviewService._available_file_path(preview_dir, safe_name)

        shutil.copy2(source_path, target_path)
        CssPreviewService._set_css_preview_file_name(
            file_name,
            os.path.basename(target_path),
            scope,
            account_id,
        )

        return target_path

    @staticmethod
    def _extract_userstyles_world_style_id(url: str):
        match = re.search(r"userstyles\.world/api/style/(\d+)\.user\.css", url)
        if not match:
            return None
        return match.group(1)

    @staticmethod
    def _download_preview_image(url: str):
        request = urllib.request.Request(url, headers={"User-Agent": "ZapZap/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.read(CssPreviewService.MAX_PREVIEW_DOWNLOAD_SIZE + 1)
        except urllib.error.URLError:
            return None

    @staticmethod
    def try_auto_attach_userstyle_preview(
        source_url: str,
        css_file_name: str,
        scope: str,
        account_id=None,
    ):
        style_id = CssPreviewService._extract_userstyles_world_style_id(source_url)
        if not style_id:
            return False

        preview_dir = CssPreviewService._css_preview_dir(scope, account_id)
        for index in (0, 1):
            preview_url = f"https://userstyles.world/preview/{style_id}/{index}.webp"
            image_data = CssPreviewService._download_preview_image(preview_url)
            if not image_data:
                continue

            if len(image_data) > CssPreviewService.MAX_PREVIEW_DOWNLOAD_SIZE:
                continue

            suggested = f"{os.path.splitext(css_file_name)[0]}-preview.webp"
            safe_name = CssPreviewService._sanitize_file_name(suggested, "webp")
            target_path = CssPreviewService._available_file_path(preview_dir, safe_name)
            try:
                with open(target_path, "wb") as file_handle:
                    file_handle.write(image_data)
            except OSError:
                continue

            CssPreviewService._set_css_preview_file_name(
                css_file_name,
                os.path.basename(target_path),
                scope,
                account_id,
            )
            return True

        return False

    @staticmethod
    def on_css_file_deleted(file_name: str, scope: str, account_id=None):
        mapping = CssPreviewService._read_css_preview_map(scope, account_id)
        preview_file_name = mapping.pop(file_name, None)
        CssPreviewService._write_css_preview_map(scope, mapping, account_id)
        if not preview_file_name:
            return

        CssPreviewService._remove_preview_file_if_unreferenced(
            scope,
            preview_file_name,
            account_id,
        )

    @staticmethod
    def on_css_file_renamed(old_file_name: str, new_file_name: str, scope: str, account_id=None):
        mapping = CssPreviewService._read_css_preview_map(scope, account_id)
        if old_file_name not in mapping:
            return

        preview_file_name = mapping.pop(old_file_name)
        mapping[new_file_name] = preview_file_name
        CssPreviewService._write_css_preview_map(scope, mapping, account_id)
