import os

from gettext import gettext as _

from PyQt6.QtCore import Qt, QUrl, QEvent, QTimer
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from zapzap.services.CssPreviewService import CssPreviewService
from zapzap.services.CustomizationsManager import CustomizationsManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_customizations import Ui_PageCustomizations


class PageCustomizations(QWidget, Ui_PageCustomizations):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.current_scope = CustomizationsManager.SCOPE_GLOBAL
        self.current_account_id = None
        self._updating_asset_lists = False
        self._preview_pixmap = None
        self._configure_asset_tables()
        self._configure_scope()
        self._configure_signals()
        self._refresh_current_account()
        self._load_scope()

    def _configure_asset_tables(self):
        for table in (self.css_files, self.js_files):
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setStretchLastSection(False)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            table.setColumnWidth(0, 90)

    def _configure_scope(self):
        self.scope_combo.clear()
        self.scope_combo.addItem(_("Global"), CustomizationsManager.SCOPE_GLOBAL)
        self.scope_combo.addItem(_("Current account"), CustomizationsManager.SCOPE_ACCOUNT)

    def _configure_signals(self):
        self.scope_combo.currentIndexChanged.connect(self._on_scope_changed)
        self.inherit_checkbox.toggled.connect(self._toggle_account_override_ui)

        self.btn_save.clicked.connect(self._save)
        self.btn_save_reload.clicked.connect(self._save_and_reload)
        self.btn_reload.clicked.connect(self._reload_pages)

        self._connect_asset_action_signals(
            CustomizationsManager.TYPE_CSS,
            self.btn_css_import,
            self.btn_css_import_url,
            self.btn_css_create,
            self.btn_css_edit,
            self.btn_css_folder,
            self.btn_css_delete,
        )
        self._connect_asset_action_signals(
            CustomizationsManager.TYPE_JS,
            self.btn_js_import,
            self.btn_js_import_url,
            self.btn_js_create,
            self.btn_js_edit,
            self.btn_js_folder,
            self.btn_js_delete,
        )

        self.css_files.itemChanged.connect(
            lambda item: self._handle_asset_toggle(item, CustomizationsManager.TYPE_CSS)
        )
        self.css_files.currentItemChanged.connect(self._on_css_selected_for_preview)
        self.js_files.itemChanged.connect(
            lambda item: self._handle_asset_toggle(item, CustomizationsManager.TYPE_JS)
        )

        self.css_preview_placeholder_upload_button.clicked.connect(self._upload_css_preview_image)
        self.css_preview_replace_button.clicked.connect(self._upload_css_preview_image)
        self.css_preview_image_page.installEventFilter(self)

    def _connect_asset_action_signals(
        self,
        asset_type: str,
        import_button,
        import_url_button,
        create_button,
        edit_button,
        open_folder_button,
        delete_button,
    ):
        import_button.clicked.connect(lambda: self._import_asset(asset_type))
        import_url_button.clicked.connect(lambda: self._import_asset_from_url(asset_type))
        create_button.clicked.connect(lambda: self._create_asset(asset_type))
        edit_button.clicked.connect(lambda: self._edit_selected_asset(asset_type))
        open_folder_button.clicked.connect(lambda: self._open_assets_folder(asset_type))
        delete_button.clicked.connect(lambda: self._delete_selected_asset(asset_type))

    def _browser(self):
        app = QApplication.instance()
        if not app or not hasattr(app, "getWindow"):
            return None

        window = app.getWindow()
        if not window or not hasattr(window, "browser"):
            return None

        return window.browser

    def _current_webview(self):
        browser = self._browser()
        if not browser:
            return None
        return browser.current_webview()

    def _find_webview_by_user_id(self, user_id):
        browser = self._browser()
        if not browser:
            return None

        for index in range(browser.pages.count()):
            webview = browser.pages.widget(index)
            if webview and webview.user and webview.user.id == user_id and webview.user.enable:
                return webview

        return None

    def _target_webview_for_scope(self):
        if self.current_scope == CustomizationsManager.SCOPE_GLOBAL:
            return self._current_webview()

        if self.current_account_id is None:
            return None

        return self._find_webview_by_user_id(self.current_account_id)

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

        self._toggle_account_override_ui()
        self._refresh_asset_lists()

    def _toggle_account_override_ui(self):
        is_account_scope = self.current_scope == CustomizationsManager.SCOPE_ACCOUNT
        is_inherit = self.inherit_checkbox.isChecked()
        allow_edit = not (is_account_scope and is_inherit)

        for widget in (
            self.css_enabled,
            self.js_enabled,
            self.btn_css_import,
            self.btn_js_import,
            self.btn_css_import_url,
            self.btn_js_import_url,
            self.btn_css_create,
            self.btn_js_create,
            self.btn_css_edit,
            self.btn_js_edit,
            self.btn_css_folder,
            self.btn_js_folder,
            self.btn_css_delete,
            self.btn_js_delete,
            self.css_files,
            self.js_files,
            self.css_preview_placeholder_upload_button,
            self.css_preview_replace_button,
        ):
            widget.setEnabled(allow_edit)

    def _dialog_options(self):
        if SettingsManager.get("system/DontUseNativeDialog", False):
            return QFileDialog.Option.DontUseNativeDialog
        return QFileDialog.Option(0)

    def _is_account_scope_locked(self):
        return (
            self.current_scope == CustomizationsManager.SCOPE_ACCOUNT
            and self.inherit_checkbox.isChecked()
        )

    def _table_widget_for_asset(self, asset_type: str):
        return (
            self.css_files
            if asset_type == CustomizationsManager.TYPE_CSS
            else self.js_files
        )

    def _asset_toggle_message(self, asset_type: str, enabled: bool):
        if asset_type == CustomizationsManager.TYPE_CSS:
            return _("CSS file enabled: {}") if enabled else _("CSS file disabled: {}")

        return (
            _("JavaScript file enabled: {}")
            if enabled
            else _("JavaScript file disabled: {}")
        )

    def _show_userstyle_or_default_error(self, error: Exception, default_message: str):
        if str(error) == "invalid-userstyle-target":
            self._show_feedback(_("This userstyle does not target WhatsApp Web."))
            return

        self._show_feedback(default_message)

    def _show_import_url_error(self, asset_type: str, reason: str):
        if reason == "invalid-url-scheme":
            self._show_feedback(_("Only HTTPS URLs are allowed."))
            return

        if reason == "download-too-large":
            self._show_feedback(_("Download is too large."))
            return

        if reason == "invalid-userstyle-target":
            self._show_feedback(_("This userstyle does not target WhatsApp Web."))
            return

        if asset_type == CustomizationsManager.TYPE_CSS:
            self._show_feedback(_("Could not download CSS from URL."))
        else:
            self._show_feedback(_("Could not download JavaScript from URL."))

    def _schedule_preview_fit(self):
        if self.css_preview_stack.currentIndex() != 1 or not self._preview_pixmap:
            return

        QTimer.singleShot(0, self._update_preview_image_fit)

    def _selected_row(self, asset_type: str):
        table_widget = self._table_widget_for_asset(asset_type)
        row = table_widget.currentRow()
        if row < 0:
            self._show_feedback(_("Select a file first."))
            return None
        return row

    def _selected_file_name(self, asset_type: str, show_feedback: bool = True):
        table_widget = self._table_widget_for_asset(asset_type)
        selected_row = (
            self._selected_row(asset_type)
            if show_feedback
            else table_widget.currentRow()
        )
        if selected_row is None:
            return None

        if selected_row < 0:
            return None

        file_item = table_widget.item(selected_row, 1)
        if not file_item:
            return None

        return file_item.text()

    def _set_css_preview_placeholder(self, message):
        self.css_preview_placeholder.setText(message)
        self.css_preview_replace_button.setVisible(False)
        self.css_preview_stack.setCurrentIndex(0)
        self._preview_pixmap = None
        self.css_preview_image.clear()

    def _disable_css_preview(self):
        self.css_preview_placeholder_upload_button.setVisible(False)
        self._set_css_preview_placeholder(_("Select a CSS file to preview."))

    def _update_preview_image_fit(self):
        if not self._preview_pixmap:
            return

        target_size = self.css_preview_image_page.size()
        if target_size.width() < 20 or target_size.height() < 20:
            QTimer.singleShot(0, self._update_preview_image_fit)
            return

        pixmap = self._preview_pixmap
        if pixmap.width() <= target_size.width() and pixmap.height() <= target_size.height():
            self.css_preview_image.setPixmap(pixmap)
            return

        scaled = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.css_preview_image.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_preview_image_fit()

    def _on_css_selected_for_preview(self, _current, _previous):
        if self._updating_asset_lists:
            return

        self._apply_selected_css_to_preview()

    def _apply_selected_css_to_preview(self):
        file_name = self._selected_file_name(CustomizationsManager.TYPE_CSS, show_feedback=False)
        if not file_name:
            self.css_preview_placeholder_upload_button.setVisible(False)
            self._set_css_preview_placeholder(_("Select a CSS file to preview."))
            return

        preview_path = CssPreviewService.get_css_preview_path(
            file_name,
            self.current_scope,
            self.current_account_id,
        )
        if not preview_path:
            self.css_preview_placeholder_upload_button.setVisible(True)
            self._set_css_preview_placeholder(_("No preview available."))
            return

        pixmap = QPixmap(preview_path)
        if pixmap.isNull():
            self.css_preview_placeholder_upload_button.setVisible(True)
            self._set_css_preview_placeholder(_("Could not load preview image."))
            return

        self.css_preview_placeholder_upload_button.setVisible(False)
        self._preview_pixmap = pixmap
        self.css_preview_stack.setCurrentIndex(1)
        self._schedule_preview_fit()

    def eventFilter(self, watched, event):
        if watched != self.css_preview_image_page:
            return super().eventFilter(watched, event)

        event_type = event.type()
        if event_type == QEvent.Type.Leave:
            self.css_preview_replace_button.setVisible(False)
            return super().eventFilter(watched, event)

        if event_type != QEvent.Type.Enter:
            return super().eventFilter(watched, event)

        if self.css_preview_stack.currentIndex() != 1:
            return super().eventFilter(watched, event)

        self.css_preview_replace_button.setVisible(True)

        return super().eventFilter(watched, event)

    def _missing_url_message(self, asset_type: str):
        if asset_type == CustomizationsManager.TYPE_CSS:
            return _("Enter a CSS HTTPS URL.")

        return _("Enter a JavaScript HTTPS URL.")

    def _import_asset_from_url_by_type(self, asset_type: str, url: str, file_name: str):
        if asset_type == CustomizationsManager.TYPE_CSS:
            return CustomizationsManager.import_css_from_url(
                url,
                self.current_scope,
                self.current_account_id,
                file_name,
            )

        return CustomizationsManager.import_js_from_url(
            url,
            self.current_scope,
            self.current_account_id,
            file_name,
        )

    def _show_imported_file_feedback(self, asset_type: str, source_url: str, imported_file: str):
        if asset_type != CustomizationsManager.TYPE_CSS:
            self._show_feedback(_("File imported: {}").format(imported_file))
            return

        has_preview = CssPreviewService.try_auto_attach_userstyle_preview(
            source_url,
            imported_file,
            self.current_scope,
            self.current_account_id,
        )
        if has_preview:
            self._show_feedback(_("File imported: {}").format(imported_file))
            return

        self._show_feedback(
            _("File imported: {}. No preview found, upload one manually.").format(imported_file)
        )

    def _upload_css_preview_image(self):
        file_name = self._selected_file_name(CustomizationsManager.TYPE_CSS)
        if not file_name:
            return

        image_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            _("Select preview image"),
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.gif *.bmp)",
            options=self._dialog_options(),
        )
        if not image_path:
            return

        try:
            CssPreviewService.set_css_preview_from_file(
                file_name,
                image_path,
                self.current_scope,
                self.current_account_id,
            )
        except ValueError:
            self._show_feedback(_("Could not set preview image."))
            return

        self._apply_selected_css_to_preview()
        self._show_feedback(_("Preview image updated."))

    def _ask_import_from_url(self, asset_type: str):
        extension = "css" if asset_type == CustomizationsManager.TYPE_CSS else "js"

        dialog = QDialog(self)
        dialog.setWindowTitle(_("Import from URL"))
        dialog.resize(480, 120)
        dialog.setMinimumSize(480, 120)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        url_input = QLineEdit(dialog)
        if asset_type == CustomizationsManager.TYPE_CSS:
            url_input.setPlaceholderText(_("https://example.com/theme.user.css"))
        else:
            url_input.setPlaceholderText(_("https://example.com/script.js"))

        file_name_input = QLineEdit(dialog)
        file_name_input.setPlaceholderText(
            _("Optional file name (e.g. 10-custom.{})").format(extension)
        )

        form_layout.addRow(_("URL"), url_input)
        form_layout.addRow(_("File name"), file_name_input)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(dialog)
        button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None, None

        return url_input.text().strip(), file_name_input.text().strip()

    def _open_asset_editor(self, asset_type: str, title: str, initial_name: str, initial_content: str):
        extension = "css" if asset_type == CustomizationsManager.TYPE_CSS else "js"

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(760, 520)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        file_name_input = QLineEdit(dialog)
        file_name_input.setText(initial_name)
        file_name_input.setPlaceholderText(_("custom.{}").format(extension))
        form_layout.addRow(_("File name"), file_name_input)
        layout.addLayout(form_layout)

        editor = QTextEdit(dialog)
        editor.setPlainText(initial_content)
        layout.addWidget(editor)

        button_box = QDialogButtonBox(dialog)
        button_box.addButton(QDialogButtonBox.StandardButton.Save)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None, None

        return file_name_input.text().strip(), editor.toPlainText()

    def _import_asset(self, asset_type: str):
        if self._is_account_scope_locked():
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

        try:
            CustomizationsManager.import_asset_file(
                file_path,
                self.current_scope,
                asset_type,
                self.current_account_id,
            )
        except ValueError as error:
            self._show_userstyle_or_default_error(error, _("Could not import file."))
            return

        self._refresh_asset_lists()
        self._show_feedback(_("File imported successfully."))

    def _import_asset_from_url(self, asset_type: str):
        if self._is_account_scope_locked():
            return

        url, file_name = self._ask_import_from_url(asset_type)
        if url is None:
            return

        if not url:
            self._show_feedback(self._missing_url_message(asset_type))
            return

        try:
            target_path = self._import_asset_from_url_by_type(asset_type, url, file_name)
        except ValueError as error:
            self._show_import_url_error(asset_type, str(error))
            return

        self._refresh_asset_lists()
        imported_file = os.path.basename(target_path)
        self._show_imported_file_feedback(asset_type, url, imported_file)

    def _create_asset(self, asset_type: str):
        if self._is_account_scope_locked():
            return

        default_name = "custom.css" if asset_type == CustomizationsManager.TYPE_CSS else "custom.js"
        file_name, content = self._open_asset_editor(
            asset_type,
            _("Create file"),
            default_name,
            "",
        )
        if file_name is None:
            return

        if not file_name:
            self._show_feedback(_("File name cannot be empty."))
            return

        try:
            target_path = CustomizationsManager.create_asset_file(
                file_name,
                content,
                self.current_scope,
                asset_type,
                self.current_account_id,
            )
        except ValueError as error:
            self._show_userstyle_or_default_error(error, _("Could not create file."))
            return

        self._refresh_asset_lists()
        self._show_feedback(_("File created: {}").format(os.path.basename(target_path)))

    def _edit_selected_asset(self, asset_type: str):
        if self._is_account_scope_locked():
            return

        old_file_name = self._selected_file_name(asset_type)
        if not old_file_name:
            return

        try:
            initial_content = CustomizationsManager.read_asset_file_content(
                old_file_name,
                self.current_scope,
                asset_type,
                self.current_account_id,
            )
        except ValueError:
            self._show_feedback(_("Could not open file for editing."))
            return

        title = _("Edit CSS: {}") if asset_type == CustomizationsManager.TYPE_CSS else _("Edit JavaScript: {}")
        new_file_name, content = self._open_asset_editor(
            asset_type,
            title.format(old_file_name),
            old_file_name,
            initial_content,
        )
        if new_file_name is None:
            return

        if not new_file_name:
            self._show_feedback(_("File name cannot be empty."))
            return

        try:
            final_name = old_file_name
            if new_file_name != old_file_name:
                final_name = CustomizationsManager.rename_asset_file(
                    old_file_name,
                    new_file_name,
                    self.current_scope,
                    asset_type,
                    self.current_account_id,
                )

            CustomizationsManager.write_asset_file_content(
                final_name,
                content,
                self.current_scope,
                asset_type,
                self.current_account_id,
            )
        except ValueError as error:
            self._show_userstyle_or_default_error(error, _("Could not save file."))
            return

        self._refresh_asset_lists()
        self._show_feedback(_("File saved: {}").format(final_name))

    def _open_assets_folder(self, asset_type: str):
        path = CustomizationsManager.get_assets_dir(
            self.current_scope,
            asset_type,
            self.current_account_id,
        )
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _refresh_asset_lists(self):
        self._updating_asset_lists = True
        try:
            for asset_type, table_widget in (
                (CustomizationsManager.TYPE_CSS, self.css_files),
                (CustomizationsManager.TYPE_JS, self.js_files),
            ):
                file_names = CustomizationsManager.list_asset_file_names(
                    self.current_scope,
                    asset_type,
                    self.current_account_id,
                )
                table_widget.setRowCount(0)
                for file_name in file_names:
                    row = table_widget.rowCount()
                    table_widget.insertRow(row)

                    enabled_item = QTableWidgetItem()
                    enabled_flags = enabled_item.flags()
                    enabled_flags |= Qt.ItemFlag.ItemIsUserCheckable
                    enabled_flags &= ~Qt.ItemFlag.ItemIsEditable
                    enabled_item.setFlags(enabled_flags)
                    enabled = CustomizationsManager.is_asset_file_enabled(
                        file_name,
                        self.current_scope,
                        asset_type,
                        self.current_account_id,
                    )
                    enabled_item.setCheckState(
                        Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
                    )

                    file_item = QTableWidgetItem(file_name)
                    file_flags = file_item.flags()
                    file_flags &= ~Qt.ItemFlag.ItemIsEditable
                    file_item.setFlags(file_flags)

                    table_widget.setItem(row, 0, enabled_item)
                    table_widget.setItem(row, 1, file_item)
        finally:
            self._updating_asset_lists = False

        self._apply_selected_css_to_preview()

    def _reload_target_webview(self, silent=False):
        target_webview = self._target_webview_for_scope()
        if not target_webview:
            return False

        target_webview.load_page()
        if not silent:
            self._show_feedback(_("Reload complete."))

        return True

    def _handle_asset_toggle(self, item, asset_type: str):
        if self._updating_asset_lists:
            return

        if item.column() != 0:
            return

        enabled = item.checkState() == Qt.CheckState.Checked
        table_widget = self._table_widget_for_asset(asset_type)
        file_item = table_widget.item(item.row(), 1)
        if not file_item:
            return

        file_name = file_item.text()
        CustomizationsManager.set_asset_file_enabled(
            file_name,
            enabled,
            self.current_scope,
            asset_type,
            self.current_account_id,
        )

        message = self._asset_toggle_message(asset_type, enabled)

        self._show_feedback(
            _("{}. Save and reload to apply changes.").format(message.format(file_name))
        )

    def _delete_selected_asset(self, asset_type: str):
        if self._is_account_scope_locked():
            return

        file_name = self._selected_file_name(asset_type)
        if not file_name:
            return

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
            self._show_feedback(_("File deleted."))
        else:
            self._show_feedback(_("Could not delete file."))

    def _save(self, show_feedback=True):
        self._disable_css_preview()

        scope = self.current_scope
        account_id = self.current_account_id

        if scope == CustomizationsManager.SCOPE_ACCOUNT:
            CustomizationsManager.set_inherit(account_id, self.inherit_checkbox.isChecked())

        if not (
            scope == CustomizationsManager.SCOPE_ACCOUNT and self.inherit_checkbox.isChecked()
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

        if show_feedback:
            self._show_feedback(_("Customizations saved. Reload pages to apply changes."))

    def _save_and_reload(self):
        self._save(show_feedback=False)
        self._reload_pages()

    def _reload_pages(self):
        self._disable_css_preview()
        reloaded = self._reload_target_webview(silent=True)
        if reloaded:
            self._show_feedback(_("All pages reloaded."))

    def _show_feedback(self, message):
        self.feedback_label.setText(message)

        current = self._current_webview()
        if current and current.page():
            try:
                current.page().show_toast(message, 2200)
            except Exception:
                pass
