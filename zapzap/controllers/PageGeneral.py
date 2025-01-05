from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication

from zapzap.services.DictionariesManager import DictionariesManager


class PageGeneral(QWidget):
    """Classe para gerenciar a página de configurações de aparência."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_general.ui", self)
        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        """Carrega as configurações iniciais da interface."""
        self.dic_path.setText(DictionariesManager.get_path())
        self.spell_comboBox.addItems(DictionariesManager.list())
        print("Idioma do sistema:", DictionariesManager.get_system_language())
        self.spell_comboBox.setCurrentText(
            DictionariesManager.get_current_dict())

    def _configure_signals(self):
        """Conecta os sinais dos widgets aos respectivos manipuladores."""
        self.spell_comboBox.textActivated.connect(self._handle_spellcheck)

    def _handle_spellcheck(self, lang):
        print('Linguagem selecionada:', lang)
        DictionariesManager.set_lang(lang)
        QApplication.instance().getWindow().browser.update_spellcheck()
