"""Safe application-wide Qt proxy configuration."""

from __future__ import annotations

from dataclasses import dataclass
from gettext import gettext as _
import logging
from typing import Any

from PyQt6 import QtNetwork

from zapzap.core.config.settings_manager import SettingsManager


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProxyApplyResult:
    """Outcome of applying persisted proxy settings to Qt."""

    success: bool
    proxy_type: str
    error: str | None = None


class ProxyManager:
    PROXY_TYPES = {
        "NoProxy": (
            QtNetwork.QNetworkProxy.ProxyType.NoProxy,
            _("No proxying is used."),
        ),
        "DefaultProxy": (
            QtNetwork.QNetworkProxy.ProxyType.DefaultProxy,
            _("Proxy is determined based on the system proxy."),
        ),
        "Socks5Proxy": (
            QtNetwork.QNetworkProxy.ProxyType.Socks5Proxy,
            _("Socks5 proxying is used."),
        ),
        "HttpProxy": (
            QtNetwork.QNetworkProxy.ProxyType.HttpProxy,
            _("HTTP transparent proxying is used."),
        ),
        "HttpCachingProxy": (
            QtNetwork.QNetworkProxy.ProxyType.HttpCachingProxy,
            _("Proxying for HTTP requests only."),
        ),
        "FtpCachingProxy": (
            QtNetwork.QNetworkProxy.ProxyType.FtpCachingProxy,
            _("Proxying for FTP requests only."),
        ),
    }
    SERVER_PROXY_TYPES = {
        "Socks5Proxy",
        "HttpProxy",
        "HttpCachingProxy",
        "FtpCachingProxy",
    }

    @staticmethod
    def _configuration(user_id=None) -> tuple[str, bool, str]:
        prefix = f"{user_id}/proxy/" if user_id else "proxy/"
        proxy_type = SettingsManager.get(f"{prefix}proxyType", "NoProxy")
        enabled = bool(SettingsManager.get(f"{prefix}proxyEnable", False))

        if user_id and not enabled:
            prefix = "proxy/"
            proxy_type = SettingsManager.get("proxy/proxyType", "NoProxy")
            enabled = bool(SettingsManager.get("proxy/proxyEnable", False))

        if not isinstance(proxy_type, str) or proxy_type not in ProxyManager.PROXY_TYPES:
            raise ValueError("unsupported proxy type")
        return proxy_type, enabled, prefix

    @staticmethod
    def _server_value(prefix: str, key: str) -> Any:
        return SettingsManager.get(f"{prefix}{key}", "")

    @staticmethod
    def _build_proxy(proxy_type: str, enabled: bool, prefix: str):
        proxy = QtNetwork.QNetworkProxy()
        effective_type = proxy_type if enabled else "DefaultProxy"
        proxy.setType(ProxyManager.PROXY_TYPES[effective_type][0])

        if not enabled or proxy_type not in ProxyManager.SERVER_PROXY_TYPES:
            return proxy

        host = ProxyManager._server_value(prefix, "hostName")
        port = ProxyManager._server_value(prefix, "port")
        if not isinstance(host, str) or not host.strip():
            raise ValueError("missing proxy host")
        try:
            port_number = int(port)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("invalid proxy port") from error
        if not 1 <= port_number <= 65535:
            raise ValueError("invalid proxy port")

        proxy.setHostName(host.strip())
        proxy.setPort(port_number)
        for key, setter in (
            ("user", proxy.setUser),
            ("password", proxy.setPassword),
        ):
            value = ProxyManager._server_value(prefix, key)
            if value not in (None, ""):
                setter(str(value))
        return proxy

    @staticmethod
    def apply(profile=None, user_id=None) -> ProxyApplyResult:
        """Apply a proxy atomically, preserving the current proxy on failure."""
        proxy_type = "NoProxy"
        try:
            proxy_type, enabled, prefix = ProxyManager._configuration(user_id)
            proxy = ProxyManager._build_proxy(proxy_type, enabled, prefix)
            QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
        except ValueError as error:
            logger.warning(
                "Invalid proxy settings; preserving the current Qt proxy"
            )
            return ProxyApplyResult(False, proxy_type, str(error))
        except Exception as error:
            logger.exception(
                "Failed to apply proxy settings; preserving the current Qt proxy"
            )
            return ProxyApplyResult(False, proxy_type, str(error))

        scope = "account" if user_id else "global"
        logger.info(
            "Applied %s proxy configuration: type=%s enabled=%s",
            scope,
            proxy_type,
            enabled,
        )
        return ProxyApplyResult(True, proxy_type)

    @staticmethod
    def get_proxy_description(proxy_type_key):
        """Return the translated description of a supported proxy type."""
        return _(
            ProxyManager.PROXY_TYPES.get(
                proxy_type_key,
                ProxyManager.PROXY_TYPES["NoProxy"],
            )[1]
        )
