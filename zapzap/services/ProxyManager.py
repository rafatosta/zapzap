import logging
from PyQt6 import QtNetwork
from PyQt6.QtWidgets import QApplication
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager


class ProxyManager:
    PROXY_TYPES = {
        'NoProxy': (QtNetwork.QNetworkProxy.ProxyType.NoProxy, _("No proxying is used.")),
        'DefaultProxy': (QtNetwork.QNetworkProxy.ProxyType.DefaultProxy, _("Proxy is determined based on the system proxy.")),
        'Socks5Proxy': (QtNetwork.QNetworkProxy.ProxyType.Socks5Proxy, _("Socks5 proxying is used.")),
        'HttpProxy': (QtNetwork.QNetworkProxy.ProxyType.HttpProxy, _("HTTP transparent proxying is used.")),
        'HttpCachingProxy': (QtNetwork.QNetworkProxy.ProxyType.HttpCachingProxy, _("Proxying for HTTP requests only.")),
        'FtpCachingProxy': (QtNetwork.QNetworkProxy.ProxyType.FtpCachingProxy, _("Proxying for FTP requests only.")),
    }

    

    @staticmethod
    def apply(profile=None, user_id=None):
        """Aplica as configurações de proxy.
        Se user_id for fornecido, usa as configurações específicas desse usuário.
        Se profile for fornecido, aplica o proxy apenas nesse perfil.
        """

        logger = logging.getLogger(__name__)
        prefix = f"{user_id}/proxy/" if user_id else "proxy/"

        proxy_type_key = SettingsManager.get(f"{prefix}proxyType", "NoProxy")
        proxy_enable = SettingsManager.get(f"{prefix}proxyEnable", False)

        # Se for proxy por conta e estiver desabilitado, tenta o global
        if user_id and not proxy_enable:
            proxy_type_key = SettingsManager.get("proxy/proxyType", "NoProxy")
            proxy_enable = SettingsManager.get("proxy/proxyEnable", False)
            prefix = "proxy/"

        proxy = QtNetwork.QNetworkProxy()
        
        if proxy_enable and proxy_type_key != 'NoProxy':
            proxy.setType(ProxyManager.PROXY_TYPES.get(
                proxy_type_key, ProxyManager.PROXY_TYPES['NoProxy'])[0])
            host_name = SettingsManager.get(f"{prefix}hostName", "")
            port = SettingsManager.get(f"{prefix}port", "")
            user = SettingsManager.get(f"{prefix}user", "")
            password = SettingsManager.get(f"{prefix}password", "")

            if host_name:
                proxy.setHostName(host_name)
            if port:
                try:
                    proxy.setPort(int(port))
                except ValueError:
                    pass
            if user:
                proxy.setUser(user)
            if password:
                proxy.setPassword(password)

        # Application-wide proxy is the only option in this version of Qt WebEngine
        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
        
        # Log the application
        if user_id:
            logger.info(f"Global proxy switched to match account {user_id}: {proxy_type_key}")
        else:
            logger.info(f"Global proxy applied: {proxy_type_key}")

        # Consolidando as informações no log
        logger.info(f"Proxy applied to {'profile' if profile else 'application'}: {proxy_type_key} (enabled={proxy_enable})")

    @staticmethod
    def get_proxy_description(proxy_type_key):
        """Retorna a descrição do tipo de proxy."""
        return _(ProxyManager.PROXY_TYPES.get(proxy_type_key, ProxyManager.PROXY_TYPES['NoProxy'])[1])
