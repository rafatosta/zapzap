from PyQt6.QtWidgets import QWidget, QApplication, QStyle
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl, QLocale
from zapzap.services.SetupManager import SetupManager
from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.TranslationManager import TranslationManager
from zapzap.views.ui_page_general import Ui_PageGeneral

from gettext import gettext as _


class PageGeneral(QWidget, Ui_PageGeneral):
    """Gerencia a página de configurações gerais de aparência e idioma."""

    FLATPAK_OVERRIDE_COMMAND = "flatpak override --user --filesystem=home com.rtosta.zapzap"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._configure_ui()

        self._load_settings()
        self._configure_signals()

    def _configure_ui(self):

        self.btn_path_download.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.btn_restore_path_download.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        self.btn_path_spell.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.btn_default_path_spell.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogResetButton))
        self.flatpak_permissions_groupBox.hide()

        if SetupManager._is_flatpak:
            self.btn_wayland.setDisabled(True)
            self.btn_wayland.setToolTip(
                _("Use Flatseal to change this mode of execution"))

            self.flatpak_permissions_groupBox.show()

    def _load_settings(self):
        """
        Carrega as configurações iniciais da página:
        - Exibe o caminho atual dos dicionários.
        - Popula o combobox de idiomas disponíveis.
        - Define o idioma atual configurado.
        """
        dictionaries_path = DictionariesManager.get_path()
        self.dic_path.setText(dictionaries_path)

        self.spellchecker_groupBox.setChecked(
            SettingsManager.get("system/spellCheckers", True)
        )

        # Limpa e repopula o combobox de idiomas
        self.spell_comboBox.clear()
        self.spell_comboBox.addItems(DictionariesManager.list())

        current_language = DictionariesManager.get_current_dict()

        self.spell_comboBox.setCurrentText(current_language)

        self.download_path.setText(DownloadManager.get_path())

        self.btn_confirm_in_close.setChecked(
            SettingsManager.get("system/confirm_on_close", False))
        self.btn_quit_in_close.setChecked(
            SettingsManager.get("system/quit_in_close", False))
        self.btn_start_background.setChecked(
            SettingsManager.get("system/start_background", False))
        self.btn_start_system.setChecked(
            SettingsManager.get("system/start_system", False))

        self.btn_wayland.setChecked(
            SettingsManager.get("system/wayland", False))

        self.dontUseNativeDialog.setChecked(
            SettingsManager.get("system/DontUseNativeDialog", False))

        self._load_interface_languages()

        self.flatpak_command_input.setText(self.FLATPAK_OVERRIDE_COMMAND)

    def _configure_signals(self):
        """
        Conecta os sinais dos widgets aos respectivos manipuladores:
        - Alteração do idioma do corretor ortográfico.
        - Alteração do diretório de dicionários.
        """

        self.spellchecker_groupBox.toggled.connect(
            lambda toggled: self._handle_toggled_spellcheck(toggled))

        self.interface_language_comboBox.currentIndexChanged.connect(
            self._handle_interface_language
        )
        self.spell_comboBox.textActivated.connect(self._handle_spellcheck)
        self.btn_path_spell.clicked.connect(self._handle_path_spell)
        self.btn_default_path_spell.clicked.connect(
            self._handle_default_folder_spell)
        self.btn_path_download.clicked.connect(self._handle_path_download)
        self.btn_restore_path_download.clicked.connect(
            self._handle_restore_path_download)

        self.btn_confirm_in_close.clicked.connect(
            lambda: SettingsManager.set("system/confirm_on_close", self.btn_confirm_in_close.isChecked()))
        self.btn_quit_in_close.clicked.connect(
            lambda: SettingsManager.set("system/quit_in_close", self.btn_quit_in_close.isChecked()))
        self.btn_start_background.clicked.connect(
            lambda: SettingsManager.set("system/start_background", self.btn_start_background.isChecked()))
        self.btn_start_system.clicked.connect(self._handle_autostart)

        self.btn_wayland.clicked.connect(
            lambda: SettingsManager.set("system/wayland", self.btn_wayland.isChecked()))

        self.dontUseNativeDialog.clicked.connect(
            lambda: SettingsManager.set("system/DontUseNativeDialog", self.dontUseNativeDialog.isChecked()))

        self.btn_copy_flatpak_command.clicked.connect(
            lambda: QApplication.clipboard().setText(self.FLATPAK_OVERRIDE_COMMAND)
        )

        self.btn_open_flatseal.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
            )
        )

    def _load_interface_languages(self):
        self.interface_language_comboBox.blockSignals(True)
        self.interface_language_comboBox.clear()
        self.interface_language_comboBox.addItem(
            _("System default"), TranslationManager.SYSTEM_LANGUAGE
        )

        for language in TranslationManager.list_available_languages():
            self.interface_language_comboBox.addItem(
                self._language_label(language), language
            )

        current_language = TranslationManager.get_current_language()
        index = self.interface_language_comboBox.findData(current_language)
        if index < 0:
            index = 0
        self.interface_language_comboBox.setCurrentIndex(index)
        self.interface_language_comboBox.blockSignals(False)

    def _language_label(self, language):
        locale = QLocale(language)
        language_name = QLocale.languageToString(locale.language())
        territory_name = QLocale.territoryToString(locale.territory())

        if territory_name:
            return f"{language_name} ({territory_name}) - {language}"
        return f"{language_name} - {language}"

    def _handle_interface_language(self, *_args):
        language = self.interface_language_comboBox.currentData()
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
        """
        Manipula a mudança de idioma para o corretor ortográfico.
        Atualiza a configuração e notifica o navegador.

        Args:
            lang (str): Idioma selecionado.
        """
        print(f"Linguagem selecionada: {lang}")
        DictionariesManager.set_lang(lang)
        self._update_browser_spellcheck()

    def _handle_path_spell(self):
        """
        Manipula a mudança do diretório de dicionários para um novo caminho.
        Atualiza as configurações e o navegador.
        """
        new_path = DownloadManager.open_folder_dialog(self)
        if new_path:
            print(f'Novo diretório: {new_path}')
            self.dic_path.setText(new_path)
            DictionariesManager.set_spell_folder(new_path)

            # Atualiza o combobox e o navegador
            self._load_settings()
            self._update_browser_spellcheck()

    def _handle_autostart(self):
        """Cria e remove o arquivo para iniciar com o sistema."""
        SettingsManager.set("system/start_system",
                            self.btn_start_system.isChecked())
        AutostartManager.create_desktop_file(self.btn_start_system.isChecked())

    def _handle_default_folder_spell(self):
        """
        Restaura o diretório de dicionários para o caminho padrão.
        Atualiza as configurações e o navegador.
        """
        new_path = DictionariesManager.restore_default_path()
        print(f'Restaurando diretório: {new_path}')
        self.dic_path.setText(new_path)

        # Atualiza o combobox e o navegador
        self._load_settings()
        self._update_browser_spellcheck()

    def _update_browser_spellcheck(self):
        """
        Notifica o navegador sobre a atualização do idioma ou diretório do corretor ortográfico.
        """
        QApplication.instance().getWindow().browser.update_spellcheck()

    def _handle_path_download(self):
        """
        Manipula a mudança do diretório de downloads.
        """
        new_path = DownloadManager.open_folder_dialog(self)
        if new_path:
            DownloadManager.set_path(new_path)
            self.download_path.setText(DownloadManager.get_path())

    def _handle_restore_path_download(self):
        """
        Restaura o diretório de downloads para o padrão.
        """
        DownloadManager.restore_path()
        self.download_path.setText(DownloadManager.get_path())
