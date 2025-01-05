import os
from PyQt6.QtCore import QLocale

from zapzap.config.SetupManager import SetupManager
from zapzap.services.SettingsManager import SettingsManager


class DictionariesManager:
    """Gerencia os dicionários """

    QTWEBENGINE_DICTIONARIES_PATH = "/usr/share/qt6/qtwebengine_dictionaries"

    QTWEBENGINE_DICTIONARIES_PATH_FLATPAK = "/run/host/usr/share/qt6/qtwebengine_dictionaries"

    @staticmethod
    def list_files():
        dictionaries_path = DictionariesManager.get_path()
        if dictionaries_path and os.path.isdir(dictionaries_path):
            print("Linguagens disponíveis:")
            for file in os.listdir(dictionaries_path):
                if file.endswith(".bdic"):
                    print(file.replace(".bdic", ""))
        else:
            print("Caminho não encontrado ou inválido.")

    @staticmethod
    def get_path():
        if SetupManager._is_flatpak:
            return DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH_FLATPAK

        return DictionariesManager.QTWEBENGINE_DICTIONARIES_PATH

    @staticmethod
    def list() -> list:
        dict_list = []
        dictionaries_path = DictionariesManager.get_path()
        if dictionaries_path and os.path.isdir(dictionaries_path):
            for file in os.listdir(dictionaries_path):
                if file.endswith(".bdic"):
                    dict_list.append(file.replace(".bdic", ""))
        else:
            print("Caminho não encontrado ou inválido.")

        return dict_list

    @staticmethod
    def set_lang(lang):
        SettingsManager.set("system/spellCheckLanguage", lang)
        # Avisa para o browser

    @staticmethod
    def get_current_dict():
        return SettingsManager.get("system/spellCheckLanguage", DictionariesManager.get_system_language())

    def get_system_language():
        return QLocale.system().name()
