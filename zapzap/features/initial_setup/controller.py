"""Controller for the first-run initial setup dialog."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtCore import QLocale
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.initial_setup.model import InitialSetupModel
from zapzap.features.initial_setup.view import InitialSetupView


class InitialSetupController(InitialSetupView):
    """Coordinates onboarding state, navigation, and persistence."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = InitialSetupModel()
        self.current_step = 0
        self._load_settings()
        self._connect_signals()
        self.set_step(0)

    @classmethod
    def should_show(cls) -> bool:
        return not InitialSetupModel.is_completed()

    def _connect_signals(self):
        self.btn_back.clicked.connect(self._previous_step)
        self.btn_next.clicked.connect(self._next_step)
        self.btn_finish.clicked.connect(self._finish)
        self.btn_skip.clicked.connect(self._skip)
        self.btn_download_path.clicked.connect(self._choose_download_path)
        self.btn_copy_flatpak_command.clicked.connect(
            lambda: QApplication.clipboard().setText(
                self.model.FLATPAK_OVERRIDE_COMMAND
            )
        )
        self.btn_open_flatseal.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
            )
        )
        for index, button in enumerate(self.step_buttons):
            button.clicked.connect(lambda _checked=False, step=index: self._go_to_step(step))
        self.notifications_enabled.toggled.connect(self._sync_notification_controls)
        self.tray_enabled.toggled.connect(self._sync_tray_controls)
        self.spellcheck_enabled.toggled.connect(self._sync_dictionary_controls)

    def _load_settings(self):
        self._load_languages()
        self._load_theme()
        self.notifications_enabled.setChecked(
            self.model.notifications_enabled
        )
        self.notify_photo.setChecked(
            self.model.notification_show_photo
        )
        self.notify_name.setChecked(
            self.model.notification_show_name
        )
        self.notify_preview.setChecked(
            self.model.notification_show_message_preview
        )
        self.tray_enabled.setChecked(self.model.tray_icon_enabled)
        self.tray_counter.setChecked(
            self.model.tray_notification_counter
        )
        self.keep_background.setChecked(
            self.model.keep_running_in_background
        )
        self.confirm_close.setChecked(
            self.model.confirm_on_close
        )
        self.start_system.setChecked(
            self.model.autostart_enabled
        )
        self.start_minimized.setChecked(
            self.model.start_minimized
        )
        self.download_path.setText(self.model.download_path())
        self.configure_flatpak_permissions(self.model.is_flatpak())
        self.flatpak_command_input.setText(self.model.FLATPAK_OVERRIDE_COMMAND)
        self.spellcheck_enabled.setChecked(
            self.model.spellcheck_enabled
        )
        self._load_dictionaries()
        self.permission_microphone.setChecked(
            self.model.microphone_permission_enabled()
        )
        self.permission_camera.setChecked(
            self.model.camera_permission_enabled()
        )
        self.permission_screen.setChecked(
            self.model.screen_contents_permission_enabled()
        )
        self.webrtc_shield.setChecked(
            self.model.webrtc_shield_enabled
        )
        self._sync_notification_controls()
        self._sync_tray_controls()
        self._sync_dictionary_controls()

    def _load_languages(self):
        self.language_combo.clear()
        self.language_combo.addItem(_("System default"), TranslationManager.SYSTEM_LANGUAGE)
        for language in self.model.available_languages():
            self.language_combo.addItem(self._language_label(language), language)
        current_language = self.model.current_language()
        index = self.language_combo.findData(current_language)
        self.language_combo.setCurrentIndex(index if index >= 0 else 0)

    def _load_theme(self):
        theme = self.model.current_theme()
        theme_map = {
            ThemeManager.Type.Auto.value: self.theme_auto,
            ThemeManager.Type.Light.value: self.theme_light,
            ThemeManager.Type.Dark.value: self.theme_dark,
        }
        theme_map.get(theme, self.theme_auto).setChecked(True)

    def _load_dictionaries(self):
        dictionaries = self.model.dictionaries()
        self.dictionary_combo.clear()
        self.dictionary_combo.addItems(dictionaries)
        current_dictionary = self.model.current_dictionary()
        if current_dictionary:
            self.dictionary_combo.setCurrentText(current_dictionary)
        has_dictionaries = bool(dictionaries)
        self.dictionary_row.setVisible(has_dictionaries)
        self.dictionary_hint.setVisible(not has_dictionaries)
        if not has_dictionaries:
            self.spellcheck_enabled.setChecked(False)

    def _language_label(self, language: str) -> str:
        if language == TranslationManager.ENGLISH_LANGUAGE:
            return f"{_('English')} - {language}"
        locale = QLocale(language)
        language_name = QLocale.languageToString(locale.language())
        territory_name = QLocale.territoryToString(locale.territory())
        if territory_name:
            return f"{language_name} ({territory_name}) - {language}"
        return f"{language_name} - {language}"

    def _selected_theme(self) -> str:
        if self.theme_light.isChecked():
            return ThemeManager.Type.Light.value
        if self.theme_dark.isChecked():
            return ThemeManager.Type.Dark.value
        return ThemeManager.Type.Auto.value

    def _sync_notification_controls(self):
        enabled = self.notifications_enabled.isChecked()
        for checkbox in (self.notify_photo, self.notify_name, self.notify_preview):
            checkbox.setEnabled(enabled)

    def _sync_tray_controls(self):
        enabled = self.tray_enabled.isChecked()
        self.tray_counter.setEnabled(enabled)
        if not enabled and self.keep_background.isChecked():
            self.keep_background.setChecked(False)
        self.keep_background.setEnabled(enabled)

    def _sync_dictionary_controls(self):
        enabled = self.spellcheck_enabled.isChecked() and self.dictionary_combo.count() > 0
        self.dictionary_combo.setEnabled(enabled)

    def _choose_download_path(self):
        path = self.model.open_download_folder_dialog(self)
        if path:
            self.download_path.setText(path)

    def _go_to_step(self, step: int):
        if 0 <= step < self.pages.count():
            self.current_step = step
            self.set_step(self.current_step)

    def _next_step(self):
        self._go_to_step(self.current_step + 1)

    def _previous_step(self):
        self._go_to_step(self.current_step - 1)

    def _skip(self):
        self.model.mark_completed()
        self.accept()

    def _finish(self):
        self._save_settings()
        self.model.mark_completed()
        self.accept()

    def _save_settings(self):
        self.model.set_language(self.language_combo.currentData())
        self.model.set_theme(self._selected_theme())
        self.model.notifications_enabled = self.notifications_enabled.isChecked()
        self.model.notification_show_photo = self.notify_photo.isChecked()
        self.model.notification_show_name = self.notify_name.isChecked()
        self.model.notification_show_message_preview = self.notify_preview.isChecked()
        self.model.tray_icon_enabled = self.tray_enabled.isChecked()
        self.model.tray_notification_counter = self.tray_counter.isChecked()
        self.model.refresh_tray()
        self.model.keep_running_in_background = self.keep_background.isChecked()
        self.model.confirm_on_close = self.confirm_close.isChecked()
        self.model.set_autostart(self.start_system.isChecked())
        self.model.start_minimized = self.start_minimized.isChecked()
        if self.download_path.text():
            self.model.set_download_path(self.download_path.text())
        self.model.spellcheck_enabled = self.spellcheck_enabled.isChecked()
        if self.spellcheck_enabled.isChecked() and self.dictionary_combo.currentText():
            self.model.set_dictionary(self.dictionary_combo.currentText())
        self.model.set_microphone_permission(self.permission_microphone.isChecked())
        self.model.set_camera_permission(self.permission_camera.isChecked())
        self.model.set_screen_contents_permission(self.permission_screen.isChecked())
        self.model.webrtc_shield_enabled = self.webrtc_shield.isChecked()
