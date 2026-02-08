from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox

from zapzap.services.CustomizationsManager import CustomizationsManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_customizations import Ui_PageCustomizations


class PageCustomizations(QWidget, Ui_PageCustomizations):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.current_scope = CustomizationsManager.SCOPE_GLOBAL
        self.current_account_id = None

        self._configure_scope()
        self._configure_signals()
        self._refresh_current_account()
        self._load_scope()

    def _configure_scope(self):
        self.scope_combo.clear()
        self.scope_combo.addItem(_("Global"), CustomizationsManager.SCOPE_GLOBAL)
        self.scope_combo.addItem(_("Current account"), CustomizationsManager.SCOPE_ACCOUNT)

    def _configure_signals(self):
        self.scope_combo.currentIndexChanged.connect(self._on_scope_changed)
        self.inherit_checkbox.toggled.connect(self._toggle_account_override_ui)
        self.btn_save.clicked.connect(self._save)
        self.btn_apply_css.clicked.connect(self._apply_css_now)
        self.btn_reload.clicked.connect(self._reload_pages)
        self.btn_css_import.clicked.connect(
            lambda: self._import_asset(CustomizationsManager.TYPE_CSS)
        )
        self.btn_js_import.clicked.connect(
            lambda: self._import_asset(CustomizationsManager.TYPE_JS)
        )
        self.btn_css_folder.clicked.connect(
            lambda: self._open_assets_folder(CustomizationsManager.TYPE_CSS)
        )
        self.btn_js_folder.clicked.connect(
            lambda: self._open_assets_folder(CustomizationsManager.TYPE_JS)
        )
        self.btn_css_delete.clicked.connect(
            lambda: self._delete_selected_asset(CustomizationsManager.TYPE_CSS)
        )
        self.btn_js_delete.clicked.connect(
            lambda: self._delete_selected_asset(CustomizationsManager.TYPE_JS)
        )

    def _browser(self):
        return QApplication.instance().getWindow().browser

    def _current_webview(self):
        browser = self._browser()
        if not browser:
            return None
        return browser.current_webview()

    def _refresh_current_account(self):
        current = self._current_webview()
        if current and current.user:
            self.current_account_id = current.user.id
            name = current.user.name if current.user.name else _("Unnamed account")
            self.account_label.setText(
                _("Current account: {} ({})").format(name, current.user.id)
            )
        else:
            self.current_account_id = None
            self.account_label.setText(_("Current account: unavailable"))

    def _on_scope_changed(self):
        self._refresh_current_account()
        self.current_scope = self.scope_combo.currentData()
        if (
            self.current_scope == CustomizationsManager.SCOPE_ACCOUNT
            and self.current_account_id is None
        ):
            self.scope_combo.setCurrentIndex(0)
            self.current_scope = CustomizationsManager.SCOPE_GLOBAL
        self._load_scope()

    def _load_scope(self):
        scope = self.current_scope
        account_id = self.current_account_id
        is_account_scope = scope == CustomizationsManager.SCOPE_ACCOUNT

        self.inherit_checkbox.setVisible(is_account_scope)
        self.account_scope_hint_label.setVisible(is_account_scope)

        if is_account_scope:
            self.inherit_checkbox.setChecked(CustomizationsManager.get_inherit(account_id))
        else:
            self.inherit_checkbox.setChecked(False)

        self.css_enabled.setChecked(
            CustomizationsManager.get_scope_enabled(
                scope, CustomizationsManager.TYPE_CSS, account_id
            )
        )
        self.js_enabled.setChecked(
            CustomizationsManager.get_scope_enabled(
                scope, CustomizationsManager.TYPE_JS, account_id
            )
        )

        self.css_editor.setPlainText(
            CustomizationsManager.get_scope_inline(
                scope, CustomizationsManager.TYPE_CSS, account_id
            )
        )
        self.js_editor.setPlainText(
            CustomizationsManager.get_scope_inline(
                scope, CustomizationsManager.TYPE_JS, account_id
            )
        )

        self._toggle_account_override_ui()
        self._refresh_asset_lists()

    def _toggle_account_override_ui(self):
        is_account_scope = self.current_scope == CustomizationsManager.SCOPE_ACCOUNT
        is_inherit = self.inherit_checkbox.isChecked()
        allow_edit = not (is_account_scope and is_inherit)

        for widget in (
            self.css_enabled,
            self.js_enabled,
            self.css_editor,
            self.js_editor,
            self.btn_css_import,
            self.btn_js_import,
            self.btn_css_folder,
            self.btn_js_folder,
            self.btn_css_delete,
            self.btn_js_delete,
        ):
            widget.setEnabled(allow_edit)

    def _dialog_options(self):
        if SettingsManager.get("system/DontUseNativeDialog", False):
            return QFileDialog.Option.DontUseNativeDialog
        return QFileDialog.Option(0)

    def _import_asset(self, asset_type: str):
        if (
            self.current_scope == CustomizationsManager.SCOPE_ACCOUNT
            and self.inherit_checkbox.isChecked()
        ):
            return

        extension = "*.css" if asset_type == CustomizationsManager.TYPE_CSS else "*.js"
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            _("Select file"),
            "",
            extension,
            options=self._dialog_options(),
        )

        if not file_path:
            return

        CustomizationsManager.import_asset_file(
            file_path,
            self.current_scope,
            asset_type,
            self.current_account_id,
        )

        self._refresh_asset_lists()
        self._apply_css_now()
        self._show_feedback(_("File imported successfully."))

    def _open_assets_folder(self, asset_type: str):
        path = CustomizationsManager.get_assets_dir(
            self.current_scope,
            asset_type,
            self.current_account_id,
        )
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _refresh_asset_lists(self):
        self.css_files.clear()
        self.css_files.addItems(
            CustomizationsManager.list_asset_file_names(
                self.current_scope,
                CustomizationsManager.TYPE_CSS,
                self.current_account_id,
            )
        )

        self.js_files.clear()
        self.js_files.addItems(
            CustomizationsManager.list_asset_file_names(
                self.current_scope,
                CustomizationsManager.TYPE_JS,
                self.current_account_id,
            )
        )

    def _delete_selected_asset(self, asset_type: str):
        if (
            self.current_scope == CustomizationsManager.SCOPE_ACCOUNT
            and self.inherit_checkbox.isChecked()
        ):
            return

        list_widget = self.css_files if asset_type == CustomizationsManager.TYPE_CSS else self.js_files
        selected = list_widget.currentItem()
        if not selected:
            self._show_feedback(_("Select a file to delete."))
            return

        file_name = selected.text()
        file_kind = _("CSS") if asset_type == CustomizationsManager.TYPE_CSS else _("JS")
        answer = QMessageBox.question(
            self,
            _("Confirm deletion"),
            _("Delete selected {} file: {}?").format(file_kind, file_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self._show_feedback(_("Deletion cancelled."))
            return

        deleted = CustomizationsManager.delete_asset_file(
            file_name,
            self.current_scope,
            asset_type,
            self.current_account_id,
        )
        if deleted:
            self._refresh_asset_lists()
            self._apply_css_now()
            self._show_feedback(_("File deleted."))
        else:
            self._show_feedback(_("Could not delete file."))

    def _save(self):
        scope = self.current_scope
        account_id = self.current_account_id

        if scope == CustomizationsManager.SCOPE_ACCOUNT:
            CustomizationsManager.set_inherit(account_id, self.inherit_checkbox.isChecked())

        if not (
            scope == CustomizationsManager.SCOPE_ACCOUNT
            and self.inherit_checkbox.isChecked()
        ):
            CustomizationsManager.set_scope_enabled(
                scope,
                CustomizationsManager.TYPE_CSS,
                self.css_enabled.isChecked(),
                account_id,
            )
            CustomizationsManager.set_scope_enabled(
                scope,
                CustomizationsManager.TYPE_JS,
                self.js_enabled.isChecked(),
                account_id,
            )
            CustomizationsManager.set_scope_inline(
                scope,
                CustomizationsManager.TYPE_CSS,
                self.css_editor.toPlainText(),
                account_id,
            )
            CustomizationsManager.set_scope_inline(
                scope,
                CustomizationsManager.TYPE_JS,
                self.js_editor.toPlainText(),
                account_id,
            )

        self._apply_css_now()
        self._show_feedback(
            _("Customizations saved. Reload pages to apply JavaScript changes.")
        )

    def _apply_css_now(self):
        browser = self._browser()
        browser.apply_custom_css_all_pages()

    def _reload_pages(self):
        self._save()
        browser = self._browser()
        browser.reload_pages()
        self._show_feedback(_("All pages reloaded."))

    def _show_feedback(self, message):
        self.feedback_label.setText(message)

        current = self._current_webview()
        if current and current.page():
            try:
                current.page().show_toast(message, 2200)
            except Exception:
                pass
