import os
import shutil

from PyQt6.QtCore import QStandardPaths

from zapzap.services.SettingsManager import SettingsManager


class CustomizationsManager:
    SCOPE_GLOBAL = "global"
    SCOPE_ACCOUNT = "account"

    TYPE_CSS = "css"
    TYPE_JS = "js"

    @staticmethod
    def _base_dir():
        return os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            ),
            "customizations",
        )

    @staticmethod
    def _to_text(value):
        if value is None:
            return ""
        return value if isinstance(value, str) else str(value)

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
    def get_scope_inline(scope: str, asset_type: str, account_id=None) -> str:
        if scope == CustomizationsManager.SCOPE_GLOBAL:
            return CustomizationsManager._to_text(SettingsManager.get(
                CustomizationsManager._global_key(asset_type, "inline"), ""
            ))

        return CustomizationsManager._to_text(SettingsManager.get(
            CustomizationsManager._account_key(account_id, asset_type, "inline"), ""
        ))

    @staticmethod
    def set_scope_inline(scope: str, asset_type: str, content: str, account_id=None):
        if scope == CustomizationsManager.SCOPE_GLOBAL:
            SettingsManager.set(
                CustomizationsManager._global_key(asset_type, "inline"), content
            )
            return

        SettingsManager.set(
            CustomizationsManager._account_key(account_id, asset_type, "inline"), content
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
    def delete_asset_file(file_name: str, scope: str, asset_type: str, account_id=None):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)
        target_path = os.path.normpath(os.path.join(assets_dir, file_name))

        if not target_path.startswith(os.path.normpath(assets_dir) + os.sep):
            return False

        if not os.path.isfile(target_path):
            return False

        try:
            os.remove(target_path)
            return True
        except OSError:
            return False

    @staticmethod
    def import_asset_file(source_path: str, scope: str, asset_type: str, account_id=None):
        assets_dir = CustomizationsManager.get_assets_dir(scope, asset_type, account_id)

        base_name = os.path.basename(source_path)
        name, ext = os.path.splitext(base_name)
        expected = ".css" if asset_type == CustomizationsManager.TYPE_CSS else ".js"
        if ext.lower() != expected:
            raise ValueError(f"Invalid file type for {asset_type}: {base_name}")

        target_path = os.path.join(assets_dir, base_name)
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join(assets_dir, f"{name}_{counter}{ext}")
            counter += 1

        shutil.copy2(source_path, target_path)
        return target_path

    @staticmethod
    def _read_files_content(scope: str, asset_type: str, account_id=None):
        chunks = []
        for file_path in CustomizationsManager.list_asset_files(scope, asset_type, account_id):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    chunks.append(f.read())
            except OSError:
                continue
        return "\n\n".join(chunks)

    @staticmethod
    def _build_scope_asset(scope: str, asset_type: str, account_id=None):
        enabled = CustomizationsManager.get_scope_enabled(scope, asset_type, account_id)
        if not enabled:
            return ""

        inline_text = CustomizationsManager.get_scope_inline(scope, asset_type, account_id)
        files_text = CustomizationsManager._read_files_content(scope, asset_type, account_id)

        parts = [part for part in (inline_text, files_text) if part]
        return "\n\n".join(parts)

    @staticmethod
    def build_effective_assets(account_id=None):
        global_css = CustomizationsManager._build_scope_asset(
            CustomizationsManager.SCOPE_GLOBAL,
            CustomizationsManager.TYPE_CSS,
        )
        global_js = CustomizationsManager._build_scope_asset(
            CustomizationsManager.SCOPE_GLOBAL,
            CustomizationsManager.TYPE_JS,
        )

        if account_id is None:
            return global_css, global_js

        if CustomizationsManager.get_inherit(account_id):
            return global_css, global_js

        account_css = CustomizationsManager._build_scope_asset(
            CustomizationsManager.SCOPE_ACCOUNT,
            CustomizationsManager.TYPE_CSS,
            account_id,
        )
        account_js = CustomizationsManager._build_scope_asset(
            CustomizationsManager.SCOPE_ACCOUNT,
            CustomizationsManager.TYPE_JS,
            account_id,
        )

        css_parts = [part for part in (global_css, account_css) if part]
        js_parts = [part for part in (global_js, account_js) if part]
        return "\n\n".join(css_parts), "\n\n".join(js_parts)

    @staticmethod
    def css_injection_script(css_text: str):
        escaped = (
            css_text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("${", "\\${")
        )

        return f"""
            (function() {{
                var id = 'zapzap-custom-css';
                var style = document.getElementById(id);
                if (!style) {{
                    style = document.createElement('style');
                    style.id = id;
                    document.head.appendChild(style);
                }}
                style.textContent = `{escaped}`;
            }})();
        """

    @staticmethod
    def clear_css_script():
        return """
            (function() {
                var style = document.getElementById('zapzap-custom-css');
                if (style) {
                    style.remove();
                }
            })();
        """
