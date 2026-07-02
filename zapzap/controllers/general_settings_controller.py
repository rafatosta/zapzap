"""Controller for the general settings page."""

from gettext import gettext as _

from PyQt6.QtCore import QLocale, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from zapzap.models.general_settings_model import GeneralSettingsModel
from zapzap.views.pages.general_settings_view import GeneralSettingsView


class GeneralSettingsController(QWidget):
    """Coordinates general settings state and actions for the view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = GeneralSettingsModel()
        self.view = GeneralSettingsView(self)
        self._setup_ui()
        self._configure_ui()
        self._load_settings()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

    def _configure_ui(self):
        self.view.configure_flatpak(self.model.is_flatpak())

    def _load_settings(self):
        self.view.dic_path.setText(self.model.get_dictionaries_path())
        self.view.spellchecker_groupBox.checkbox.setChecked(
            self.model.get_setting("system/spellCheckers", True)
        )

        self.view.spell_comboBox.clear()
        self.view.spell_comboBox.addItems(self.model.list_dictionaries())
        self.view.spell_comboBox.setCurrentText(self.model.get_current_dictionary())

        self.view.download_path.setText(self.model.get_download_path())
        self.view.btn_confirm_in_close.setChecked(
            self.model.get_setting("system/confirm_on_close", False)
        )
        self.view.btn_quit_in_close.setChecked(
            self.model.get_setting("system/quit_in_close", False)
        )
        self.view.btn_start_background.setChecked(
            self.model.get_setting("system/start_background", False)
        )
        self.view.btn_start_system.setChecked(
            self.model.get_setting("system/start_system", False)
        )
        self.view.btn_wayland.setChecked(
            self.model.get_setting("system/wayland", False)
        )
        self.view.dontUseNativeDialog.setChecked(
            self.model.get_setting("system/DontUseNativeDialog", False)
        )

        self._load_interface_languages()
        self.view.flatpak_command_input.setText(self.model.FLATPAK_OVERRIDE_COMMAND)

    def _connect_signals(self):
        self.view.spellchecker_groupBox.checkbox.toggled.connect(
            self._handle_toggled_spellcheck
        )
        self.view.interface_language_comboBox.currentIndexChanged.connect(
            self._handle_interface_language
        )
        self.view.spell_comboBox.textActivated.connect(self._handle_spellcheck)
        self.view.btn_path_spell.clicked.connect(self._handle_path_spell)
        self.view.btn_default_path_spell.clicked.connect(
            self._handle_default_folder_spell
        )
        self.view.btn_path_download.clicked.connect(self._handle_path_download)
        self.view.btn_restore_path_download.clicked.connect(
            self._handle_restore_path_download
        )
        self.view.btn_confirm_in_close.clicked.connect(
            lambda: self.model.set_setting(
                "system/confirm_on_close",
                self.view.btn_confirm_in_close.isChecked(),
            )
        )
        self.view.btn_quit_in_close.clicked.connect(
            lambda: self.model.set_setting(
                "system/quit_in_close",
                self.view.btn_quit_in_close.isChecked(),
            )
        )
        self.view.btn_start_background.clicked.connect(
            lambda: self.model.set_setting(
                "system/start_background",
                self.view.btn_start_background.isChecked(),
            )
        )
        self.view.btn_start_system.clicked.connect(self._handle_autostart)
        self.view.btn_wayland.clicked.connect(
            lambda: self.model.set_setting(
                "system/wayland",
                self.view.btn_wayland.isChecked(),
            )
        )
        self.view.dontUseNativeDialog.clicked.connect(
            lambda: self.model.set_setting(
                "system/DontUseNativeDialog",
                self.view.dontUseNativeDialog.isChecked(),
            )
        )
        self.view.btn_copy_flatpak_command.clicked.connect(
            lambda: QApplication.clipboard().setText(
                self.model.FLATPAK_OVERRIDE_COMMAND
            )
        )
        self.view.btn_open_flatseal.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
            )
        )

    def _load_interface_languages(self):
        combo = self.view.interface_language_comboBox
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(_("System default"), "system")

        for language in self.model.list_available_languages():
            combo.addItem(self._language_label(language), language)

        current_language = self.model.get_current_language()
        index = combo.findData(current_language)
        if index < 0:
            index = 0
        combo.setCurrentIndex(index)
        combo.blockSignals(False)

    def _language_label(self, language):
        locale = QLocale(language)
        language_name = QLocale.languageToString(locale.language())
        territory_name = QLocale.territoryToString(locale.territory())

        if territory_name:
            return f"{language_name} ({territory_name}) - {language}"
        return f"{language_name} - {language}"

    def _handle_interface_language(self, *_args):
        language = self.view.interface_language_comboBox.currentData()
        self.model.set_current_language(language)
        self.model.apply_translation()
        self._retranslate_application()

    def _retranslate_application(self):
        app = QApplication.instance()
        for widget in app.allWidgets():
            retranslate = getattr(widget, "retranslateUi", None)
            if callable(retranslate):
                retranslate(widget)

        self._load_interface_languages()

    def _handle_toggled_spellcheck(self, toggled):
        self.model.set_setting("system/spellCheckers", toggled)
        self._update_browser_spellcheck()

    def _handle_spellcheck(self, language):
        self.model.set_dictionary_language(language)
        self._update_browser_spellcheck()

    def _handle_path_spell(self):
        new_path = self.model.open_folder_dialog(self)
        if new_path:
            self.view.dic_path.setText(new_path)
            self.model.set_dictionary_path(new_path)
            self._load_settings()
            self._update_browser_spellcheck()

    def _handle_autostart(self):
        self.model.set_autostart(self.view.btn_start_system.isChecked())

    def _handle_default_folder_spell(self):
        new_path = self.model.restore_dictionary_path()
        self.view.dic_path.setText(new_path)
        self._load_settings()
        self._update_browser_spellcheck()

    def _update_browser_spellcheck(self):
        QApplication.instance().getWindow().browser.update_spellcheck()

    def _handle_path_download(self):
        new_path = self.model.open_folder_dialog(self)
        if new_path:
            self.model.set_download_path(new_path)
            self.view.download_path.setText(self.model.get_download_path())

    def _handle_restore_path_download(self):
        self.view.download_path.setText(self.model.restore_download_path())
