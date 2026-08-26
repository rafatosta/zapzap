"""Copy a reviewed report and open the official GitHub issue page."""

from __future__ import annotations

import shutil
import sys
import webbrowser

from PyQt6.QtCore import QProcess, QUrl, QUrlQuery
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.core.reporting.markdown import ReportMarkdownFormatter
from zapzap.core.reporting.model import ReportDocument


class GitHubReportLauncher:
    """Local handoff only: no report content is transmitted by ZapZap."""

    NEW_ISSUE_URL = "https://github.com/rafatosta/zapzap/issues/new"

    def __init__(
        self,
        *,
        opener=None,
        browser_opener=None,
        clipboard=None,
    ):
        self._opener = opener
        self._browser_opener = browser_opener or webbrowser.open
        self._clipboard = clipboard

    @property
    def clipboard(self):
        return self._clipboard or QApplication.clipboard()

    def prepare_and_open(self, document: ReportDocument) -> bool:
        self.clipboard.setText(ReportMarkdownFormatter.format(document))
        url = QUrl(self.NEW_ISSUE_URL)
        query = QUrlQuery()
        query.addQueryItem("title", ReportMarkdownFormatter.title(document))
        url.setQuery(query)
        encoded_url = bytes(url.toEncoded()).decode("ascii")

        if self._opener is None and sys.platform.startswith("linux"):
            xdg_open = shutil.which("xdg-open")
            if xdg_open:
                try:
                    started, _process_id = QProcess.startDetached(
                        xdg_open,
                        [encoded_url],
                    )
                    if started:
                        return True
                except (OSError, RuntimeError):
                    pass

        opener = self._opener or QDesktopServices.openUrl
        try:
            if opener(url):
                return True
        except (OSError, RuntimeError):
            pass

        try:
            return bool(
                self._browser_opener(
                    encoded_url,
                    new=2,
                    autoraise=True,
                )
            )
        except (OSError, webbrowser.Error):
            return False
