"""Dedicated lifecycle for authenticated WhatsApp Web popup windows."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtCore import QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView

from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.core.diagnostics.webengine_probe import probe


class InternalWebPopup(QWebEngineView):
    """Independent view that owns a popup page from an existing profile."""

    def __init__(self, page: QWebEnginePage, on_closed, parent=None):
        super().__init__(parent)
        probe.watch(self, "popup")
        probe.watch(page, "popup-page", self)
        self._popup_page = page
        self._on_closed = on_closed
        self._cleaned_up = False
        self._programmatic_close = False
        self._page_requested_close = False
        self._stop_before_cleanup = True

        page.setParent(self)
        self.setPage(page)
        page.windowCloseRequested.connect(self._handle_page_close_requested)
        self.setWindowTitle(page.title() or "WhatsApp")
        self.titleChanged.connect(self._update_window_title)
        self.resize(960, 720)

    @property
    def popup_page(self):
        return self._popup_page

    def _update_window_title(self, title):
        self.setWindowTitle(title or "WhatsApp")

    def load_page(self):
        """Compatibility hook used by PageController's scoped fallback."""
        self.reload()

    def _handle_page_close_requested(self):
        """Honor window.close() requests emitted by the WhatsApp page."""
        with probe.scope("window_close_callback", self):
            self._page_requested_close = True
            self._stop_before_cleanup = False
            self.close()

    def close_from_host(self):
        """Close without prompting during redirects, account teardown or exit."""
        with probe.scope("popup_close_from_host", self):
            self._programmatic_close = True
            self.close()
            # Host teardown must dispose the page before its shared profile.
            self.cleanup()

    def _explain_manual_close_blocked(self) -> None:
        AlertManager.warning(
            self,
            _("Manual close unavailable"),
            _(
                "To prevent the application from becoming unresponsive, this "
                "window cannot be closed manually. Use WhatsApp's End call "
                "button. The window will close when WhatsApp requests it."
            ),
        )

    def _should_accept_close(self) -> bool:
        if self._programmatic_close or self._page_requested_close:
            return True
        self._explain_manual_close_blocked()
        return False

    def cleanup(self):
        """Stop and detach the WebEngine page exactly once."""
        with probe.scope("popup_cleanup", self):
            if self._cleaned_up:
                return
            self._cleaned_up = True

            page = self._popup_page
            self._popup_page = None
            if page is not None:
                try:
                    if self._stop_before_cleanup:
                        page.triggerAction(QWebEnginePage.WebAction.Stop)
                    probe.record("detach_page", self)
                    self.setPage(None)
                    probe.record("delete_later", page)
                    page.deleteLater()
                except RuntimeError:
                    pass

            callback = self._on_closed
            self._on_closed = None
            if callback is not None:
                callback(self)
            probe.record("delete_later", self)
            self.deleteLater()

    def closeEvent(self, event):
        with probe.scope("popup_close_event", self):
            if not self._should_accept_close():
                event.ignore()
                return

            if not self._programmatic_close:
                # Keep the page attached until Qt finishes processing the native
                # close event, then release it on the next event-loop turn.
                self._stop_before_cleanup = False
            super().closeEvent(event)
            if event.isAccepted() and not self._programmatic_close:
                QTimer.singleShot(0, self.cleanup)
