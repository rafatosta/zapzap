import os
import shutil
import json
import hashlib
import re
import urllib.error
import urllib.parse
import urllib.request

from PyQt6.QtCore import QStandardPaths

from zapzap.services.CssPreviewService import CssPreviewService
from zapzap.services.SettingsManager import SettingsManager


class CustomizationsManager:
    SCOPE_GLOBAL = "global"
    SCOPE_ACCOUNT = "account"

    TYPE_CSS = "css"
    TYPE_JS = "js"
    MAX_DOWNLOAD_SIZE = 2 * 1024 * 1024

    @staticmethod
    def _base_dir():
        return os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            ),
            "customizations",
        )

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
    def _scope_dir(scope: str, account_id=None):
        if scope == CustomizationsManager.SCOPE_GLOBAL:
            return os.path.join(CustomizationsManager._base_dir(), "global")

        account_key = str(account_id if account_id is not None else "default")
        return os.path.join(CustomizationsManager._base_dir(), "accounts", account_key)

    @staticmethod
    def get_extensions_dir():
        extensions_dir = os.path.join(CustomizationsManager._base_dir(), "extensions")
        os.makedirs(extensions_dir, exist_ok=True)
        return extensions_dir

    @staticmethod
    def get_assets_dir(scope: str, asset_type: str, account_id=None):
        assets_dir = os.path.join(
            CustomizationsManager._scope_dir(scope, account_id), asset_type
        )
        os.makedirs(assets_dir, exist_ok=True)
        return assets_dir

    @staticmethod
    def _global_key(asset_type: str, field: str):
        return f"custom/global/{asset_type}/{field}"

    @staticmethod
    def _account_key(account_id, asset_type: str, field: str):
        return f"custom/accounts/{account_id}/{asset_type}/{field}"

    @staticmethod
    def _disabled_files_key(scope: str, asset_type: str, account_id=None):
        if scope == CustomizationsManager.SCOPE_GLOBAL:
            return CustomizationsManager._global_key(asset_type, "disabled_files")

        return CustomizationsManager._account_key(account_id, asset_type, "disabled_files")

    @staticmethod
    def get_inherit(account_id) -> bool:
        return SettingsManager.get(f"custom/accounts/{account_id}/inherit", True)

    @staticmethod
    def set_inherit(account_id, inherit: bool):
        SettingsManager.set(f"custom/accounts/{account_id}/inherit", inherit)

    @staticmethod
    def get_scope_enabled(scope: str, asset_type: str, account_id=None) -> bool:
        if scope == CustomizationsManager.SCOPE_GLOBAL:
            return SettingsManager.get(
                CustomizationsManager._global_key(asset_type, "enabled"), False
            )

        return SettingsManager.get(
            CustomizationsManager._account_key(account_id, asset_type, "enabled"), False
        )

    @staticmethod
    def set_scope_enabled(scope: str, asset_type: str, enabled: bool, account_id=None):
        if scope == CustomizationsManager.SCOPE_GLOBAL:
            SettingsManager.set(
                CustomizationsManager._global_key(asset_type, "enabled"), enabled
            )
            return

        SettingsManager.set(
            CustomizationsManager._account_key(account_id, asset_type, "enabled"), enabled
        )

    @staticmethod
    def list_asset_files(scope: str, asset_type: str, account_id=None):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        ext = ".css" if asset_type == CustomizationsManager.TYPE_CSS else ".js"

        files = []
        for file_name in os.listdir(assets_dir):
            if file_name.lower().endswith(ext):
                files.append(os.path.join(assets_dir, file_name))

        files.sort(key=lambda p: os.path.basename(p).lower())
        return files

    @staticmethod
    def list_asset_file_names(scope: str, asset_type: str, account_id=None):
        return [
            os.path.basename(path)
            for path in CustomizationsManager.list_asset_files(scope, asset_type, account_id)
        ]

    @staticmethod
    def get_disabled_files(scope: str, asset_type: str, account_id=None):
        key = CustomizationsManager._disabled_files_key(scope, asset_type, account_id)
        value = SettingsManager.get(key, [])

        if isinstance(value, list):
            return [str(item) for item in value]

        if isinstance(value, str):
            return [value] if value else []

        return []

    @staticmethod
    def _set_disabled_files(scope: str, asset_type: str, file_names, account_id=None):
        key = CustomizationsManager._disabled_files_key(scope, asset_type, account_id)
        unique = sorted(set(str(name) for name in file_names if name))
        SettingsManager.set(key, unique)

    @staticmethod
    def is_asset_file_enabled(file_name: str, scope: str, asset_type: str, account_id=None):
        disabled_files = CustomizationsManager.get_disabled_files(scope, asset_type, account_id)
        return file_name not in disabled_files

    @staticmethod
    def set_asset_file_enabled(
        file_name: str,
        enabled: bool,
        scope: str,
        asset_type: str,
        account_id=None,
    ):
        disabled_files = set(
            CustomizationsManager.get_disabled_files(scope, asset_type, account_id)
        )

        if enabled:
            disabled_files.discard(file_name)
        else:
            disabled_files.add(file_name)

        CustomizationsManager._set_disabled_files(
            scope,
            asset_type,
            disabled_files,
            account_id,
        )

    @staticmethod
    def delete_asset_file(file_name: str, scope: str, asset_type: str, account_id=None):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        target_path = os.path.normpath(os.path.join(assets_dir, file_name))

        if not target_path.startswith(os.path.normpath(assets_dir) + os.sep):
            return False

        if not os.path.isfile(target_path):
            return False

        try:
            os.remove(target_path)
            CustomizationsManager.set_asset_file_enabled(
                file_name,
                True,
                scope,
                asset_type,
                account_id,
            )

            if asset_type == CustomizationsManager.TYPE_CSS:
                CssPreviewService.on_css_file_deleted(file_name, scope, account_id)
            return True
        except OSError:
            return False

    @staticmethod
    def rename_asset_file(
        old_file_name: str,
        new_file_name: str,
        scope: str,
        asset_type: str,
        account_id=None,
    ):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        old_path = os.path.normpath(os.path.join(assets_dir, old_file_name))
        extension = "css" if asset_type == CustomizationsManager.TYPE_CSS else "js"
        sanitized_name = CustomizationsManager._sanitize_file_name(new_file_name, extension)

        if not old_path.startswith(os.path.normpath(assets_dir) + os.sep):
            raise ValueError("invalid-file-name")

        if not os.path.isfile(old_path):
            raise ValueError("file-not-found")

        desired_path = os.path.normpath(os.path.join(assets_dir, sanitized_name))
        if not desired_path.startswith(os.path.normpath(assets_dir) + os.sep):
            raise ValueError("invalid-file-name")

        if os.path.normcase(desired_path) != os.path.normcase(old_path):
            desired_path = CustomizationsManager._available_file_path(
                assets_dir,
                os.path.basename(desired_path),
            )

        was_enabled = CustomizationsManager.is_asset_file_enabled(
            old_file_name,
            scope,
            asset_type,
            account_id,
        )

        try:
            os.rename(old_path, desired_path)
        except OSError as error:
            raise ValueError("rename-failed") from error

        new_file_name = os.path.basename(desired_path)
        CustomizationsManager.set_asset_file_enabled(
            old_file_name,
            True,
            scope,
            asset_type,
            account_id,
        )
        CustomizationsManager.set_asset_file_enabled(
            new_file_name,
            was_enabled,
            scope,
            asset_type,
            account_id,
        )

        if asset_type == CustomizationsManager.TYPE_CSS:
            CssPreviewService.on_css_file_renamed(
                old_file_name,
                new_file_name,
                scope,
                account_id,
            )

        return new_file_name

    @staticmethod
    def read_asset_file_content(file_name: str, scope: str, asset_type: str, account_id=None):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        target_path = os.path.normpath(os.path.join(assets_dir, file_name))

        if not target_path.startswith(os.path.normpath(assets_dir) + os.sep):
            raise ValueError("invalid-file-name")

        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as file_handle:
                return file_handle.read()
        except OSError as error:
            raise ValueError("file-read-failed") from error

    @staticmethod
    def write_asset_file_content(
        file_name: str,
        content: str,
        scope: str,
        asset_type: str,
        account_id=None,
    ):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        target_path = os.path.normpath(os.path.join(assets_dir, file_name))

        if not target_path.startswith(os.path.normpath(assets_dir) + os.sep):
            raise ValueError("invalid-file-name")

        if not os.path.isfile(target_path):
            raise ValueError("file-not-found")

        if asset_type == CustomizationsManager.TYPE_CSS:
            CustomizationsManager._normalize_css(content, strict=True)

        try:
            with open(target_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)
        except OSError as error:
            raise ValueError("file-write-failed") from error

    @staticmethod
    def import_asset_file(source_path: str, scope: str, asset_type: str, account_id=None):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)

        base_name = os.path.basename(source_path)
        _, ext = os.path.splitext(base_name)
        expected = ".css" if asset_type == CustomizationsManager.TYPE_CSS else ".js"
        if ext.lower() != expected:
            raise ValueError(f"Invalid file type for {asset_type}: {base_name}")

        if asset_type == CustomizationsManager.TYPE_CSS:
            with open(source_path, "r", encoding="utf-8", errors="replace") as file_handle:
                css_content = file_handle.read()
            CustomizationsManager._normalize_css(css_content, strict=True)

        target_path = CustomizationsManager._available_file_path(assets_dir, base_name)

        shutil.copy2(source_path, target_path)
        return target_path

    @staticmethod
    def create_asset_file(
        file_name: str,
        content: str,
        scope: str,
        asset_type: str,
        account_id=None,
    ):
        extension = "css" if asset_type == CustomizationsManager.TYPE_CSS else "js"
        final_name = CustomizationsManager._sanitize_file_name(file_name, extension)

        if asset_type == CustomizationsManager.TYPE_CSS:
            CustomizationsManager._normalize_css(content, strict=True)

        return CustomizationsManager._save_asset_content(
            content,
            scope,
            asset_type,
            account_id,
            final_name,
        )

    @staticmethod
    def import_css_from_url(url: str, scope: str, account_id=None, file_name: str = ""):
        content = CustomizationsManager._download_url_content(url)
        CustomizationsManager._normalize_css(content, strict=True)

        default_name = os.path.basename(urllib.parse.urlparse(url).path) or "style.css"
        final_name = CustomizationsManager._sanitize_file_name(
            file_name or default_name,
            "css",
        )

        return CustomizationsManager._save_asset_content(
            content,
            scope,
            CustomizationsManager.TYPE_CSS,
            account_id,
            final_name,
        )

    @staticmethod
    def import_js_from_url(url: str, scope: str, account_id=None, file_name: str = ""):
        content = CustomizationsManager._download_url_content(url)

        default_name = os.path.basename(urllib.parse.urlparse(url).path) or "script.js"
        final_name = CustomizationsManager._sanitize_file_name(
            file_name or default_name,
            "js",
        )

        return CustomizationsManager._save_asset_content(
            content,
            scope,
            CustomizationsManager.TYPE_JS,
            account_id,
            final_name,
        )

    @staticmethod
    def _download_url_content(url: str):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() != "https":
            raise ValueError("invalid-url-scheme")

        request = urllib.request.Request(url, headers={"User-Agent": "ZapZap/1.0"})

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read(CustomizationsManager.MAX_DOWNLOAD_SIZE + 1)
        except urllib.error.URLError as error:
            raise ValueError("download-failed") from error

        if len(data) > CustomizationsManager.MAX_DOWNLOAD_SIZE:
            raise ValueError("download-too-large")

        return data.decode("utf-8", errors="replace")

    @staticmethod
    def _save_asset_content(
        content: str,
        scope: str,
        asset_type: str,
        account_id,
        final_name: str,
    ):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        target_path = CustomizationsManager._available_file_path(assets_dir, final_name)

        with open(target_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)

        return target_path

    @staticmethod
    def _extract_moz_document_blocks(css_text: str):
        marker = "@-moz-document"
        if marker not in css_text:
            return []

        blocks = []
        position = 0
        text_length = len(css_text)

        while True:
            start = css_text.find(marker, position)
            if start == -1:
                break

            header_end = css_text.find("{", start)
            if header_end == -1:
                break

            depth = 1
            cursor = header_end + 1
            while cursor < text_length and depth > 0:
                char = css_text[cursor]
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                cursor += 1

            if depth != 0:
                break

            header = css_text[start:header_end]
            body = css_text[header_end + 1: cursor - 1]

            if "whatsapp.com" in header.lower():
                blocks.append(body)

            position = cursor

        return blocks

    @staticmethod
    def _normalize_css(css_text: str, strict: bool = False):
        marker = "@-moz-document"
        if marker not in css_text:
            return css_text

        blocks = CustomizationsManager._extract_moz_document_blocks(css_text)
        if not blocks:
            if strict:
                raise ValueError("invalid-userstyle-target")
            return css_text

        return "\n\n".join(block.strip() for block in blocks if block.strip())

    @staticmethod
    def _read_asset_content(file_path: str, asset_type: str):
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
                content = file_handle.read()
        except OSError:
            return ""

        if asset_type == CustomizationsManager.TYPE_CSS:
            return CustomizationsManager._normalize_css(content)
        return content

    @staticmethod
    def _build_scope_asset_entries(scope: str, asset_type: str, account_id=None):
        enabled = CustomizationsManager.get_scope_enabled(scope, asset_type, account_id)
        if not enabled:
            return []

        disabled_files = set(
            CustomizationsManager.get_disabled_files(scope, asset_type, account_id)
        )

        entries = []
        scope_name = scope if scope == CustomizationsManager.SCOPE_GLOBAL else f"account-{account_id}"

        for file_path in CustomizationsManager.list_asset_files(scope, asset_type, account_id):
            content = CustomizationsManager._read_asset_content(file_path, asset_type).strip()
            if content:
                file_name = os.path.basename(file_path)
                if file_name in disabled_files:
                    continue
                entries.append((f"{scope_name}:file:{file_name}", content))

        return entries

    @staticmethod
    def build_effective_ordered_assets(asset_type: str, account_id=None):
        global_entries = CustomizationsManager._build_scope_asset_entries(
            CustomizationsManager.SCOPE_GLOBAL,
            asset_type,
        )

        if account_id is None:
            return global_entries

        if CustomizationsManager.get_inherit(account_id):
            return global_entries

        account_entries = CustomizationsManager._build_scope_asset_entries(
            CustomizationsManager.SCOPE_ACCOUNT,
            asset_type,
            account_id,
        )

        return global_entries + account_entries

    @staticmethod
    def _entry_id(prefix: str, entry_key: str):
        digest = hashlib.sha1(entry_key.encode("utf-8")).hexdigest()[:12]
        return f"zapzap-custom-{prefix}-{digest}"

    @staticmethod
    def css_injection_script(entries):
        payload = [
            {
                "id": CustomizationsManager._entry_id("css", entry_key),
                "content": content,
            }
            for entry_key, content in entries
        ]
        payload_json = json.dumps(payload)

        return f"""
            (function() {{
                var head = document.head || document.documentElement;
                if (!head) {{
                    return;
                }}

                var attr = 'data-zapzap-custom-css';
                var payload = {payload_json};
                var managedNodes = head.querySelectorAll('style[' + attr + ']');
                for (var i = 0; i < managedNodes.length; i++) {{
                    managedNodes[i].remove();
                }}

                for (var j = 0; j < payload.length; j++) {{
                    var item = payload[j];
                    var styleNode = document.createElement('style');
                    styleNode.id = item.id;
                    styleNode.setAttribute(attr, '1');
                    styleNode.textContent = item.content;
                    head.appendChild(styleNode);
                }}
            }})();
        """

    @staticmethod
    def js_injection_script(entries):
        payload = [
            {
                "id": CustomizationsManager._entry_id("js", entry_key),
                "content": content,
            }
            for entry_key, content in entries
        ]
        payload_json = json.dumps(payload)

        return """
            (function() {
                var head = document.head || document.documentElement;
                if (!head) {
                    return;
                }

                var attr = 'data-zapzap-custom-js';
                var payload = %s;
                var managedNodes = head.querySelectorAll('script[' + attr + ']');
                for (var i = 0; i < managedNodes.length; i++) {
                    managedNodes[i].remove();
                }

                for (var j = 0; j < payload.length; j++) {
                    var item = payload[j];
                    var scriptNode = document.createElement('script');
                    scriptNode.id = item.id;
                    scriptNode.setAttribute(attr, '1');
                    scriptNode.text = item.content;
                    head.appendChild(scriptNode);
                }
            })();
        """ % payload_json
