"""Qt bridge exposed to WhatsApp Web for WA-JS result delivery."""

from __future__ import annotations

import json
import logging
from typing import Callable, Dict

from PyQt6.QtCore import QObject, pyqtSlot

logger = logging.getLogger(__name__)


class WaJsBridge(QObject):
    """Receives WA-JS call results and errors from the page."""

    def __init__(self, webview=None):
        super().__init__()
        self._webview = webview
        self._callbacks: Dict[str, Callable[[object], None]] = {}

    def register_callback(self, callback_id: str, callback: Callable[[object], None]) -> None:
        self._callbacks[callback_id] = callback

    @pyqtSlot()
    def on_ready(self) -> None:
        logger.debug("WA-JS reported ready")

    @pyqtSlot(str, str)
    def on_result(self, callback_id: str, result_json: str) -> None:
        callback = self._callbacks.pop(callback_id, None)
        if callback is None:
            return
        try:
            callback(json.loads(result_json) if result_json else None)
        except Exception:
            logger.exception("Failed to decode WA-JS result")

    @pyqtSlot(str, str)
    def on_error(self, callback_id: str, message: str) -> None:
        callback = self._callbacks.pop(callback_id, None)
        if callback is None:
            return
        logger.warning("WA-JS call failed: %s", message)
        try:
            callback({"error": message})
        except Exception:
            logger.exception("Failed to deliver WA-JS error")
