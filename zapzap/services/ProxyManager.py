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
    def apply():
        """Aplica as configurações de proxy obtidas do SettingsManager."""

        logger = logging.getLogger(__name__)

        proxy_type_key = SettingsManager.get("proxy/proxyType", "NoProxy")
        proxy_enable = SettingsManager.get("proxy/proxyEnable", False)

        proxy = QtNetwork.QNetworkProxy()
        proxy_info = [f"Proxy configurado: {proxy_type_key} ({'Habilitado' if proxy_enable else 'Desabilitado'})"]

        if proxy_enable and proxy_type_key != 'NoProxy':
            proxy.setType(ProxyManager.PROXY_TYPES.get(
                proxy_type_key, ProxyManager.PROXY_TYPES['NoProxy'])[0])
            host_name = SettingsManager.get("proxy/hostName", "")
            port = SettingsManager.get("proxy/port", "")
            user = SettingsManager.get("proxy/user", "")
            password = SettingsManager.get("proxy/password", "")

            if host_name:
                proxy.setHostName(host_name)
                proxy_info.append(f"Host: {host_name}")
            if port:
                try:
                    proxy.setPort(int(port))
                    proxy_info.append(f"Porta: {port}")
                except ValueError:
                    proxy_info.append(f"Porta inválida: {port}")
            if user:
                proxy.setUser(user)
                proxy_info.append(f"Usuário: {user}")
            if password:
                proxy.setPassword(password)
                proxy_info.append("Senha configurada.")
        else:
            proxy_info.append(f"Proxy padrão habilitado: {'Sim' if not proxy_enable else 'Não'}")

        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
        QApplication.instance().getWindow().browser.reload_pages()

        # Consolidando as informações no log
        for info in proxy_info:
            logger.info(info)

    @staticmethod
    def get_proxy_description(proxy_type_key):
        """Retorna a descrição do tipo de proxy."""
        return _(ProxyManager.PROXY_TYPES.get(proxy_type_key, ProxyManager.PROXY_TYPES['NoProxy'])[1])
