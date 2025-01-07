from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication, QStyle
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager


class PageGeneral(QWidget):
    """Gerencia a página de configurações gerais de aparência e idioma."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_general.ui", self)
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

    def _load_settings(self):
        """
        Carrega as configurações iniciais da página:
        - Exibe o caminho atual dos dicionários.
        - Popula o combobox de idiomas disponíveis.
        - Define o idioma atual configurado.
        """
        dictionaries_path = DictionariesManager.get_path()
        self.dic_path.setText(dictionaries_path)

        # Limpa e repopula o combobox de idiomas
        self.spell_comboBox.clear()
        self.spell_comboBox.addItems(DictionariesManager.list())

        system_language = DictionariesManager.get_system_language()
        current_language = DictionariesManager.get_current_dict()

        print(f"Caminho dos dicionários: {dictionaries_path}")
        print(f"Idioma do sistema: {system_language}")
        print(f"Idioma atual configurado: {current_language}")

        self.spell_comboBox.setCurrentText(current_language)

        self.download_path.setText(DownloadManager.get_path())

        self.btn_quit_in_close.setChecked(
            SettingsManager.get("system/quit_in_close", False))
        self.btn_start_background.setChecked(
            SettingsManager.get("system/start_background", False))
        self.btn_start_system.setChecked(
            SettingsManager.get("system/start_system", False))

    def _configure_signals(self):
        """
        Conecta os sinais dos widgets aos respectivos manipuladores:
        - Alteração do idioma do corretor ortográfico.
        - Alteração do diretório de dicionários.
        """
        self.spell_comboBox.textActivated.connect(self._handle_spellcheck)
        self.btn_path_spell.clicked.connect(self._handle_path_spell)
        self.btn_default_path_spell.clicked.connect(
            self._handle_default_folder_spell)
        self.btn_path_download.clicked.connect(self._handle_path_download)
        self.btn_restore_path_download.clicked.connect(
            self._handle_restore_path_download)

        self.btn_quit_in_close.clicked.connect(
            lambda: SettingsManager.set("system/quit_in_close", self.btn_quit_in_close.isChecked()))
        self.btn_start_background.clicked.connect(
            lambda: SettingsManager.set("system/start_background", self.btn_start_background.isChecked()))
        self.btn_start_system.clicked.connect(
            lambda: SettingsManager.set("system/start_system", self.btn_start_system.isChecked()))

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

    def _handle_default_folder_spell(self):
        """
        Restaura o diretório de dicionários para o caminho padrão.
        Atualiza as configurações e o navegador.
        """
        new_path = DictionariesManager.get_path_default()
        print(f'Restaurando diretório: {new_path}')
        self.dic_path.setText(new_path)
        DictionariesManager.set_spell_folder(new_path)

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
