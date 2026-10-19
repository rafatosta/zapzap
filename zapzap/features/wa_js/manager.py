"""Experimental manager for the WhatsApp Web WA-JS (WPP) integration."""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any, Callable, Optional

from PyQt6.QtWebEngineCore import QWebEngineScript

from zapzap.core.config.settings.wa_js import WaJsSettings
from zapzap.features.wa_js.bridge import WaJsBridge

logger = logging.getLogger(__name__)

BUNDLE_NAME = "zapzap_wa_js_bundle"
GLUE_NAME = "zapzap_wa_js_glue"


class WaJsManager:
    """Coordinates WA-JS settings, injection and the Qt bridge."""

    def __init__(self, webview=None, bridge=None):
        self._webview = webview
        self._bridge = bridge if bridge is not None else WaJsBridge(webview)
        self._settings = WaJsSettings()

    @property
    def webview(self):
        return self._webview

    @property
    def bridge(self) -> WaJsBridge:
        return self._bridge

    @property
    def settings(self) -> WaJsSettings:
        return self._settings

    @property
    def enabled(self) -> bool:
        return self._settings.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._settings.enabled = bool(value)

    @staticmethod
    def is_enabled() -> bool:
        return WaJsSettings().enabled

    @staticmethod
    def _read_script(path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read()
        except OSError:
            logger.exception("Failed to read WA-JS script: %s", path)
            return ""

    @classmethod
    def inject(cls, webview) -> None:
        if webview is None or webview.profile is None:
            return
        if not cls.is_enabled():
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bundle_path = os.path.join(base_dir, "..", "browser", "web", "scripts", "wppconnect-wa.js")
        bundle_source = cls._read_script(os.path.abspath(bundle_path))
        if bundle_source:
            script = QWebEngineScript()
            script.setName(BUNDLE_NAME)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            script.setRunsOnSubFrames(False)
            script.setSourceCode(bundle_source)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            webview.profile.scripts().insert(script)

        glue_path = os.path.join(base_dir, "wa_js_glue.js")
        glue_source = cls._read_script(glue_path)
        if glue_source:
            script = QWebEngineScript()
            script.setName(GLUE_NAME)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setRunsOnSubFrames(False)
            script.setSourceCode(glue_source)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            webview.profile.scripts().insert(script)

    @staticmethod
    def on_load_finished(page) -> None:
        if page is None or not WaJsManager.is_enabled():
            return
        try:
            page.runJavaScript("window.zapzapWaJs && window.zapzapWaJs;")
        except Exception:
            logger.exception("Failed to notify WA-JS load")

    def call(self, page, path: str, args: Optional[list] = None, callback: Optional[Callable[[Any], None]] = None) -> str:
        callback_id = uuid.uuid4().hex
        if callback is not None:
            self._bridge.register_callback(callback_id, callback)
        args_json = json.dumps(args or [])
        script = (
            "if (window.zapzapWaJs && typeof window.zapzapWaJs.call === 'function') {"
            "  window.zapzapWaJs.call(%s, %s, %s);"
            "}" % (json.dumps(callback_id), json.dumps(path), args_json)
        )
        if page is not None:
            page.runJavaScript(script)
        return callback_id
