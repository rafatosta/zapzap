from gettext import gettext as _

from PyQt6.QtCore import QLocale, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QStyle, QVBoxLayout, QWidget

from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SetupManager import SetupManager
from zapzap.services.TranslationManager import TranslationManager
from zapzap.views.pages.settings.general_settings_view import GeneralSettingsView


class GeneralSettingsController(QWidget):
    """Controller for general settings persistence and signals."""

    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._configure_ui()
        self._load_settings()
        self._configure_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = GeneralSettingsView(self)
        layout.addWidget(self.view)

    def _configure_ui(self):
        self.view.btn_path_download.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        )
        self.view.btn_restore_path_download.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)
        )
        self.view.btn_path_spell.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        )
        self.view.btn_default_path_spell.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)
        )
        self.view.flatpak_permissions_groupBox.hide()

        if SetupManager._is_flatpak:
            self.view.btn_wayland.setDisabled(True)
            self.view.btn_wayland.setToolTip(
                _("Use Flatseal to change this mode of execution")
            )
            self.view.flatpak_permissions_groupBox.show()

    def _load_settings(self):
        self.view.dic_path.setText(DictionariesManager.get_path())
        self.view.spellchecker_groupBox.setChecked(
            SettingsManager.get("system/spellCheckers", True)
        )

        self.view.spell_comboBox.clear()
        self.view.spell_comboBox.addItems(DictionariesManager.list())
        self.view.spell_comboBox.setCurrentText(DictionariesManager.get_current_dict())

        self.view.download_path.setText(DownloadManager.get_path())

        self.view.btn_confirm_in_close.setChecked(
            SettingsManager.get("system/confirm_on_close", False)
        )
        self.view.btn_quit_in_close.setChecked(
            SettingsManager.get("system/quit_in_close", False)
        )
        self.view.btn_start_background.setChecked(
            SettingsManager.get("system/start_background", False)
        )
        self.view.btn_start_system.setChecked(
            SettingsManager.get("system/start_system", False)
        )
        self.view.btn_wayland.setChecked(
            SettingsManager.get("system/wayland", False)
        )
        self.view.dontUseNativeDialog.setChecked(
            SettingsManager.get("system/DontUseNativeDialog", False)
        )

        self._load_interface_languages()
        self.view.flatpak_command_input.setText(self.FLATPAK_OVERRIDE_COMMAND)

    def _configure_signals(self):
        self.view.spellchecker_groupBox.toggled.connect(
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
            lambda: SettingsManager.set(
                "system/confirm_on_close",
                self.view.btn_confirm_in_close.isChecked(),
            )
        )
        self.view.btn_quit_in_close.clicked.connect(
            lambda: SettingsManager.set(
                "system/quit_in_close",
                self.view.btn_quit_in_close.isChecked(),
            )
        )
        self.view.btn_start_background.clicked.connect(
            lambda: SettingsManager.set(
                "system/start_background",
                self.view.btn_start_background.isChecked(),
            )
        )
        self.view.btn_start_system.clicked.connect(self._handle_autostart)
        self.view.btn_wayland.clicked.connect(
            lambda: SettingsManager.set(
                "system/wayland",
                self.view.btn_wayland.isChecked(),
            )
        )
        self.view.dontUseNativeDialog.clicked.connect(
            lambda: SettingsManager.set(
                "system/DontUseNativeDialog",
                self.view.dontUseNativeDialog.isChecked(),
            )
        )
        self.view.btn_copy_flatpak_command.clicked.connect(
            lambda: QApplication.clipboard().setText(self.FLATPAK_OVERRIDE_COMMAND)
        )
        self.view.btn_open_flatseal.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
            )
        )

    def _load_interface_languages(self):
        self.view.interface_language_comboBox.blockSignals(True)
        self.view.interface_language_comboBox.clear()
        self.view.interface_language_comboBox.addItem(
            _("System default"), TranslationManager.SYSTEM_LANGUAGE
        )

        for language in TranslationManager.list_available_languages():
            self.view.interface_language_comboBox.addItem(
                self._language_label(language), language
            )

        current_language = TranslationManager.get_current_language()
        index = self.view.interface_language_comboBox.findData(current_language)
        if index < 0:
            index = 0
        self.view.interface_language_comboBox.setCurrentIndex(index)
        self.view.interface_language_comboBox.blockSignals(False)

    def _language_label(self, language):
        locale = QLocale(language)
        language_name = QLocale.languageToString(locale.language())
        territory_name = QLocale.territoryToString(locale.territory())

        if territory_name:
            return f"{language_name} ({territory_name}) - {language}"
        return f"{language_name} - {language}"

    def _handle_interface_language(self, *_args):
        language = self.view.interface_language_comboBox.currentData()
        TranslationManager.set_current_language(language)
        TranslationManager.apply()
        self._retranslate_application()

    def _retranslate_application(self):
        app = QApplication.instance()
        for widget in app.allWidgets():
            retranslate = getattr(widget, "retranslateUi", None)
            if callable(retranslate):
                retranslate(widget)

        self._load_interface_languages()

    def _handle_toggled_spellcheck(self, toggled):
        SettingsManager.set("system/spellCheckers", toggled)
        self._update_browser_spellcheck()

    def _handle_spellcheck(self, lang: str):
        DictionariesManager.set_lang(lang)
        self._update_browser_spellcheck()

    def _handle_path_spell(self):
        new_path = DownloadManager.open_folder_dialog(self)
        if new_path:
            self.view.dic_path.setText(new_path)
            DictionariesManager.set_spell_folder(new_path)
            self._load_settings()
            self._update_browser_spellcheck()

    def _handle_autostart(self):
        SettingsManager.set(
            "system/start_system",
            self.view.btn_start_system.isChecked(),
        )
        AutostartManager.create_desktop_file(
            self.view.btn_start_system.isChecked()
        )

    def _handle_default_folder_spell(self):
        new_path = DictionariesManager.restore_default_path()
        self.view.dic_path.setText(new_path)
        self._load_settings()
        self._update_browser_spellcheck()

    def _update_browser_spellcheck(self):
        QApplication.instance().getWindow().browser.update_spellcheck()

    def _handle_path_download(self):
        new_path = DownloadManager.open_folder_dialog(self)
        if new_path:
            DownloadManager.set_path(new_path)
            self.view.download_path.setText(DownloadManager.get_path())

    def _handle_restore_path_download(self):
        DownloadManager.restore_path()
        self.view.download_path.setText(DownloadManager.get_path())
