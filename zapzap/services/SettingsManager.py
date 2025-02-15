from PyQt6.QtCore import QSettings
from zapzap import __appname__


class SettingsManager:
    """
    Classe para gerenciar as configurações da aplicação usando QSettings.
    Usa Singleton para manter uma única instância de QSettings.
    """

    _settings = None  # Instância única de QSettings

    @staticmethod
    def _get_settings():
        """
        Garante que a instância de QSettings seja criada uma única vez.
        :return: Instância de QSettings.
        """
        if SettingsManager._settings is None:
            # Define organização e nome da aplicação
            SettingsManager._settings = QSettings(__appname__, __appname__)
        return SettingsManager._settings

    @staticmethod
    def get(key, default=None):
        """
        Retorna o valor de uma chave de configuração.
        :param key: Chave da configuração.
        :param default: Valor padrão caso a chave não exista.
        :return: Valor da configuração.
        """
        value = SettingsManager._get_settings().value(key, default)
        # Converte strings "true"/"false" para booleanos
        if isinstance(default, bool):
            return value.lower() == 'true' if isinstance(value, str) else bool(value)
        return value

    @staticmethod
    def set(key, value):
        """
        Define um valor para uma chave de configuração.
        :param key: Chave da configuração.
        :param value: Valor a ser definido.
        """
        SettingsManager._get_settings().setValue(key, value)

    @staticmethod
    def remove(key):
        """
        Remove uma chave de configuração.
        :param key: Chave a ser removida.
        """
        SettingsManager._get_settings().remove(key)

    @staticmethod
    def clear():
        """
        Limpa todas as configurações armazenadas.
        """
        SettingsManager._get_settings().clear()

    @staticmethod
    def contains(key):
        """
        Verifica se uma chave existe nas configurações.
        :param key: Chave a ser verificada.
        :return: True se a chave existir, False caso contrário.
        """
        return SettingsManager._get_settings().contains(key)

    @staticmethod
    def all_keys():
        """
        Retorna todas as chaves de configuração.
        :return: Lista de chaves.
        """
        return SettingsManager._get_settings().allKeys()
