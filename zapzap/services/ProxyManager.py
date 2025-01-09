from PyQt6 import QtNetwork
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager


class ProxyManager:
    PROXY_TYPES = {
        'NoProxy': (QtNetwork.QNetworkProxy.ProxyType.NoProxy, _("No proxying is used")),
        'DefaultProxy': (QtNetwork.QNetworkProxy.ProxyType.DefaultProxy, _("Proxy is determined based on the application proxy set using setApplicationProxy()")),
        'Socks5Proxy': (QtNetwork.QNetworkProxy.ProxyType.Socks5Proxy, _("Socks5 proxying is used")),
        'HttpProxy': (QtNetwork.QNetworkProxy.ProxyType.HttpProxy, _("HTTP transparent proxying is used")),
        'HttpCachingProxy': (QtNetwork.QNetworkProxy.ProxyType.HttpCachingProxy, _("Proxying for HTTP requests only")),
        'FtpCachingProxy': (QtNetwork.QNetworkProxy.ProxyType.FtpCachingProxy, _("Proxying for FTP requests only")),
    }

    @staticmethod
    def apply():
        """Aplica as configurações de proxy obtidas do SettingsManager."""
        proxy_type_key = SettingsManager.get("proxy/proxyType", "NoProxy")
        proxy_enable = SettingsManager.get("proxy/proxyEnable", False)

        proxy = QtNetwork.QNetworkProxy()

        if proxy_enable and proxy_type_key != 'NoProxy':
            proxy.setType(ProxyManager.PROXY_TYPES.get(
                proxy_type_key, ProxyManager.PROXY_TYPES['NoProxy'])[0])
            host_name = SettingsManager.get("proxy/hostName", "")
            port = SettingsManager.get("proxy/port", "")
            user = SettingsManager.get("proxy/user", "")
            password = SettingsManager.get("proxy/password", "")

            if host_name:
                proxy.setHostName(host_name)
            if port:
                try:
                    proxy.setPort(int(port))
                except ValueError:
                    print(f"Porta inválida: {port}")
            if user:
                proxy.setUser(user)
            if password:
                proxy.setPassword(password)
        else:
            print('proxy_enable:', proxy_enable)
            print("Proxy default habilitado!")

        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
        print(f"Proxy configurado: {proxy_type_key} ({
              'Habilitado' if proxy_enable else 'Desabilitado'})")

    @staticmethod
    def get_proxy_description(proxy_type_key):
        """Retorna a descrição do tipo de proxy."""
        return ProxyManager.PROXY_TYPES.get(proxy_type_key, ProxyManager.PROXY_TYPES['NoProxy'])[1]

    @staticmethod
    def apply_default():
        proxy = QtNetwork.QNetworkProxy()
        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
