from gettext import gettext as _

from PyQt6.QtCore import QLocale, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLineEdit, QPushButton, QStyle, QVBoxLayout, QWidget

from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SetupManager import SetupManager
from zapzap.services.TranslationManager import TranslationManager
from zapzap.views.settings_components import (
    SettingsActionRow,
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsPathRow,
    SettingsSection,
    SettingsSelectRow,
    SettingsSwitchRow,
)


class PageGeneral(QWidget):
    """Gerencia a página de configurações gerais de aparência e idioma."""

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
        self.page = SettingsPage(
            _("General"),
            _("Manage language, startup, downloads, spell checking, and Linux integration."),
            self,
        )
        layout.addWidget(self.page)

        self._setup_language_section()
        self._setup_startup_section()
        self._setup_window_behavior_section()
        self._setup_linux_section()
        self._setup_downloads_section()
        self._setup_spellchecker_section()
        self._setup_flatpak_section()
        self.page.add_stretch()

    def _setup_language_section(self):
        section = SettingsSection(
            _("Language"),
            _("Choose the interface language used by ZapZap."),
        )
        card = SettingsCard()
        row = SettingsSelectRow(
            _("Interface language"),
            _("The interface language is applied immediately."),
        )
        self.interface_language_comboBox = row.combo
        card.add_row(row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_startup_section(self):
        section = SettingsSection(
            _("Startup"),
            _("Control how ZapZap behaves when your desktop session starts."),
        )
        card = SettingsCard()
        self.btn_start_background_row = SettingsSwitchRow(
            _("Start minimized"),
            _("Open ZapZap in the background instead of showing the main window."),
        )
        self.btn_start_system_row = SettingsSwitchRow(
            _("Start with the system"),
            _("Create or remove the desktop autostart entry."),
        )
        self.btn_start_background = self.btn_start_background_row.checkbox
        self.btn_start_system = self.btn_start_system_row.checkbox
        card.add_row(self.btn_start_background_row)
        card.add_row(self.btn_start_system_row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_window_behavior_section(self):
        section = SettingsSection(
            _("Window behavior"),
            _("Configure close behavior and native dialogs."),
        )
        card = SettingsCard()
        self.btn_confirm_in_close_row = SettingsSwitchRow(
            _("Confirm before closing the window"),
            _("Ask for confirmation before closing ZapZap."),
        )
        self.btn_quit_in_close_row = SettingsSwitchRow(
            _("Close when closing the window"),
            _("Quit the application when the main window is closed."),
        )
        self.dontUseNativeDialog_row = SettingsSwitchRow(
            _("Don't use a platform-native file dialog"),
            _("Use Qt file dialogs instead of the desktop portal or native picker."),
        )
        self.btn_confirm_in_close = self.btn_confirm_in_close_row.checkbox
        self.btn_quit_in_close = self.btn_quit_in_close_row.checkbox
        self.dontUseNativeDialog = self.dontUseNativeDialog_row.checkbox
        card.add_row(self.btn_confirm_in_close_row)
        card.add_row(self.btn_quit_in_close_row)
        card.add_row(self.dontUseNativeDialog_row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_linux_section(self):
        section = SettingsSection(
            _("Linux integration"),
            _("Options that affect how ZapZap integrates with Linux desktop sessions."),
        )
        card = SettingsCard()
        self.btn_wayland_row = SettingsSwitchRow(
            _("Wayland window system"),
            _("Enable Wayland-specific execution mode. A restart may be required."),
        )
        self.btn_wayland = self.btn_wayland_row.checkbox
        card.add_row(self.btn_wayland_row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_downloads_section(self):
        section = SettingsSection(
            _("Downloads"),
            _("Choose where downloaded files are saved."),
        )
        card = SettingsCard()
        row = SettingsPathRow(
            _("Download directory"),
            _("Set a custom folder or restore the default download location."),
            button_text="",
        )
        self.download_path = row.line_edit
        self.download_path.setReadOnly(True)
        self.btn_path_download = row.button
        self.btn_restore_path_download = QPushButton("")
        row.control.layout().addWidget(self.btn_restore_path_download)
        card.add_row(row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_spellchecker_section(self):
        section = SettingsSection(
            _("Spell checker"),
            _("Select compiled dictionaries and where ZapZap should look for them."),
        )
        card = SettingsCard()
        self.spellchecker_groupBox = SettingsSwitchRow(
            _("Enable spell checker"),
            _("Use Qt WebEngine spell checking with the selected dictionary."),
        )
        lang_row = SettingsSelectRow(
            _("Dictionary language"),
            _("Recognizes only compiled dictionaries (.bdic)."),
        )
        self.spell_comboBox = lang_row.combo
        path_row = SettingsPathRow(
            _("Dictionary directory"),
            _("Note: changing dictionaries may require restarting the browser page."),
            button_text="",
        )
        self.dic_path = path_row.line_edit
        self.dic_path.setReadOnly(True)
        self.btn_path_spell = path_row.button
        self.btn_default_path_spell = QPushButton("")
        path_row.control.layout().addWidget(self.btn_default_path_spell)
        card.add_row(self.spellchecker_groupBox)
        card.add_row(lang_row)
        card.add_row(path_row)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_flatpak_section(self):
        self.flatpak_permissions_groupBox = SettingsSection(
            _("Flatpak permissions"),
            _("Grant filesystem access if downloads, imports, or dictionaries cannot reach folders outside the sandbox."),
        )
        card = SettingsCard()
        card.add_row(SettingsInfoBox(_(
            "Flatpak sandbox: if file access fails, grant folder permissions using Flatseal or flatpak override."
        ), "warning"))
        command_row = QWidget()
        command_layout = QHBoxLayout(command_row)
        command_layout.setContentsMargins(0, 8, 0, 8)
        self.flatpak_command_input = QLineEdit()
        self.flatpak_command_input.setReadOnly(True)
        self.flatpak_command_input.setToolTip(_("Select and copy this command in your terminal"))
        self.btn_copy_flatpak_command = QPushButton(_("Copy"))
        command_layout.addWidget(self.flatpak_command_input, 1)
        command_layout.addWidget(self.btn_copy_flatpak_command)
        self.btn_open_flatseal = SettingsActionRow(
            _("Flatseal"),
            _("Flatseal is a graphical utility to review and modify permissions from your Flatpak applications."),
            _("Install Flatseal on Linux | Flathub"),
        )
        card.add_row(command_row)
        card.add_row(self.btn_open_flatseal)
        self.btn_open_flatseal = self.btn_open_flatseal.button
        self.flatpak_permissions_groupBox.add_card(card)
        self.page.add_section(self.flatpak_permissions_groupBox)

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

        self.spellchecker_groupBox.checkbox.setChecked(
            SettingsManager.get("system/spellCheckers", True)
        )

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

        self.spellchecker_groupBox.checkbox.toggled.connect(
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
