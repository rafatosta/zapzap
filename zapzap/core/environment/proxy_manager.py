"""Safe application-wide Qt proxy configuration."""

from __future__ import annotations

from dataclasses import dataclass
from gettext import gettext as _
import logging
from typing import Any

from PyQt6 import QtNetwork

from zapzap.core.config.settings.privacy import PrivacySettings
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
    EXPLICIT_PROXY_TYPES = {"Socks5Proxy", "HttpProxy"}
    _PREFIX = "proxy/"

    @staticmethod
    def _configuration() -> tuple[str, bool]:
        proxy_type = SettingsManager.get("proxy/proxyType", "NoProxy")
        enabled = bool(SettingsManager.get("proxy/proxyEnable", False))
        if (
            not isinstance(proxy_type, str)
            or proxy_type not in ProxyManager.PROXY_TYPES
        ):
            raise ValueError("unsupported proxy type")
        return proxy_type, enabled

    @staticmethod
    def _server_value(key: str) -> Any:
        return SettingsManager.get(f"{ProxyManager._PREFIX}{key}", "")

    @staticmethod
    def _build_proxy(proxy_type: str, enabled: bool):
        proxy = QtNetwork.QNetworkProxy()
        effective_type = proxy_type if enabled else "DefaultProxy"
        proxy.setType(ProxyManager.PROXY_TYPES[effective_type][0])

        if not enabled or proxy_type not in ProxyManager.SERVER_PROXY_TYPES:
            return proxy

        host = ProxyManager._server_value("hostName")
        port = ProxyManager._server_value("port")
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
            value = ProxyManager._server_value(key)
            if value not in (None, ""):
                setter(str(value))
        return proxy

    @staticmethod
    def apply() -> ProxyApplyResult:
        """Apply the sole global proxy, preserving the current proxy on failure."""
        proxy_type = "NoProxy"
        try:
            proxy_type, enabled = ProxyManager._configuration()
            proxy = ProxyManager._build_proxy(proxy_type, enabled)
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

        logger.info(
            "Applied global proxy configuration: type=%s enabled=%s",
            proxy_type,
            enabled,
        )
        return ProxyApplyResult(True, proxy_type)

    @staticmethod
    def strict_isolation_active() -> bool:
        """Return whether native strict isolation applies at this bootstrap."""
        try:
            proxy_type, enabled = ProxyManager._configuration()
            requested = PrivacySettings().strict_proxy_enabled
            if not requested:
                return False
            if not enabled or proxy_type not in ProxyManager.EXPLICIT_PROXY_TYPES:
                logger.info(
                    "Strict proxy isolation is inactive: a compatible "
                    "explicit proxy is not enabled"
                )
                return False
            # Validate the endpoint as strictly as apply(), without mutating
            # the application proxy during pre-QApplication environment setup.
            ProxyManager._build_proxy(proxy_type, enabled)
        except (TypeError, ValueError, OverflowError):
            logger.warning(
                "Strict proxy isolation is inactive: explicit proxy "
                "settings are invalid"
            )
            return False
        logger.info("Strict proxy isolation enabled for the global proxy")
        return True

    @staticmethod
    def get_proxy_description(proxy_type_key):
        """Return the translated description of a supported proxy type."""
        return _(
            ProxyManager.PROXY_TYPES.get(
                proxy_type_key,
                ProxyManager.PROXY_TYPES["NoProxy"],
            )[1]
        )
