from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget, QApplication, QStyle, QLabel, QPushButton, QHBoxLayout, QLineEdit, QMessageBox
from zapzap.services.SetupManager import SetupManager
from zapzap.services.AutostartManager import AutostartManager
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_general import Ui_PageGeneral
from zapzap.debug import crash_handler

from gettext import gettext as _


class PageGeneral(QWidget, Ui_PageGeneral):
    """Gerencia a página de configurações gerais de aparência e idioma."""

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

        if SetupManager._is_flatpak:
            self.btn_wayland.setDisabled(True)
            self.btn_wayland.setToolTip(
                _("Use Flatseal to change this mode of execution"))

            flatpak_notice = QLabel(self)
            flatpak_notice.setWordWrap(True)
            flatpak_notice.setTextFormat(Qt.TextFormat.RichText)
            flatpak_notice.setText(
                _(
                    "<b>Flatpak tip:</b> If opening PDFs, drag-and-drop, or file uploads fail, "
                    "this is usually caused by sandbox permissions. "
                    "Open <b>Flatseal</b> and grant ZapZap access to folders like "
                    "Documents, Downloads, Pictures and Videos. "
                    "You can also run: <code>flatpak override --user --filesystem=home com.rtosta.zapzap</code>."
                )
            )
            self.verticalLayout_2.insertWidget(1, flatpak_notice)

            flatpak_override_command = (
                "flatpak override --user --filesystem=home com.rtosta.zapzap"
            )

            command_layout = QHBoxLayout()
            command_input = QLineEdit(flatpak_override_command, self)
            command_input.setReadOnly(True)
            command_input.setToolTip(_("Select and copy this command in your terminal"))
            command_copy_button = QPushButton(_("Copy command"), self)
            command_copy_button.clicked.connect(
                lambda: QApplication.clipboard().setText(flatpak_override_command)
            )
            command_layout.addWidget(command_input)
            command_layout.addWidget(command_copy_button)
            self.verticalLayout_2.insertLayout(2, command_layout)

            flatseal_button = QPushButton(_("Open Flatseal page"), self)
            flatseal_button.clicked.connect(
                lambda: QDesktopServices.openUrl(
                    QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
                )
            )
            self.verticalLayout_2.insertWidget(3, flatseal_button)

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

        self._refresh_debug_logs_ui()

    def _configure_signals(self):
        """
        Conecta os sinais dos widgets aos respectivos manipuladores:
        - Alteração do idioma do corretor ortográfico.
        - Alteração do diretório de dicionários.
        """

        self.spellchecker_groupBox.toggled.connect(
            lambda toggled: self._handle_toggled_spellcheck(toggled))

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

        self.btn_open_debug_logs.clicked.connect(self._handle_open_debug_logs)
        self.btn_delete_old_debug_logs.clicked.connect(self._handle_delete_old_debug_logs)
        self.btn_delete_all_debug_logs.clicked.connect(self._handle_delete_all_debug_logs)
        self.btn_reset_settings.clicked.connect(self._handle_reset_settings)

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

    def _get_debug_logs_dir(self) -> Path:
        return Path(crash_handler.dump_dir)

    def _refresh_debug_logs_ui(self):
        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.debug_logs_path.setText(str(logs_dir))

        zip_count = len(list(logs_dir.glob("*.zip")))
        has_faulthandler = (logs_dir / "faulthandler.log").exists()
        details = _("Files: {count} crash report(s){faulthandler}.").format(
            count=zip_count,
            faulthandler=_(" + faulthandler.log") if has_faulthandler else ""
        )
        self.label_debug_logs_hint.setText(
            _("Crash reports are stored in this folder. You can open the directory or clean old files.\n{details}").format(
                details=details
            )
        )

    def _handle_open_debug_logs(self):
        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(logs_dir)))

    def _handle_delete_old_debug_logs(self):
        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)

        cutoff = datetime.now() - timedelta(days=30)
        removed = 0

        for zip_file in logs_dir.glob("*.zip"):
            modified = datetime.fromtimestamp(zip_file.stat().st_mtime)
            if modified < cutoff:
                zip_file.unlink(missing_ok=True)
                removed += 1

        QMessageBox.information(
            self,
            _("Debug logs"),
            _("Deleted {count} old crash report(s) (older than 30 days).").format(
                count=removed
            )
        )
        self._refresh_debug_logs_ui()

    def _handle_delete_all_debug_logs(self):
        confirm = QMessageBox.question(
            self,
            _("Debug logs"),
            _("Delete all crash reports and debug logs?")
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)

        removed = 0
        for item in logs_dir.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
                removed += 1

        QMessageBox.information(
            self,
            _("Debug logs"),
            _("Deleted {count} file(s).").format(count=removed)
        )
        self._refresh_debug_logs_ui()

    def _handle_reset_settings(self):
        confirm = QMessageBox.question(
            self,
            _("Reset settings"),
            _("This will delete your current settings file (.config) and requires restart. Continue?")
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        settings = SettingsManager._get_settings()
        settings_path = Path(settings.fileName())

        settings.clear()
        settings.sync()

        try:
            if settings_path.exists():
                settings_path.unlink()
        except Exception as exc:
            QMessageBox.warning(
                self,
                _("Reset settings"),
                _("Could not remove settings file:\n{error}").format(error=str(exc))
            )
            return

        SettingsManager._settings = None

        QMessageBox.information(
            self,
            _("Reset settings"),
            _("Settings were reset successfully. Please restart ZapZap.")
        )
