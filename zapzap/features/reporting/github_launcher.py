"""Copy a reviewed report and open the official GitHub issue page."""

from __future__ import annotations

from PyQt6.QtCore import QUrl, QUrlQuery
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.core.reporting.markdown import ReportMarkdownFormatter
from zapzap.core.reporting.model import ReportDocument


class GitHubReportLauncher:
    """Local handoff only: no report content is transmitted by ZapZap."""

    NEW_ISSUE_URL = "https://github.com/rafatosta/zapzap/issues/new"

    def __init__(self, *, opener=None, clipboard=None):
        self._opener = opener or QDesktopServices.openUrl
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
        return bool(self._opener(url))
