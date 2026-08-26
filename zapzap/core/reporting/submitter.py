"""Asynchronous report transmission behind per-attempt explicit consent."""

from __future__ import annotations

import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from zapzap import __report_api__

from .model import ReportDocument


class ExplicitSubmissionConsent:
    """Single-use capability issued only for a visible confirmation action."""

    def __init__(self, marker, report_json: str):
        if marker is not _CONSENT_MARKER:
            raise TypeError("submission consent must be issued by the confirmation UI")
        self._report_json = report_json
        self._used = False

    @classmethod
    def from_confirmation(cls, document: ReportDocument):
        """Issue consent in direct response to the confirmation button."""
        return cls(_CONSENT_MARKER, document.to_json())

    def consume(self, document: ReportDocument):
        if self._used or self._report_json != document.to_json():
            raise PermissionError("missing or mismatched explicit consent")
        self._used = True


_CONSENT_MARKER = object()


class _SubmissionSignals(QObject):
    succeeded = pyqtSignal(str, object)
    failed = pyqtSignal(str, str)


class _SubmissionTask(QRunnable):
    def __init__(self, report_id: str, document: ReportDocument, endpoint: str, signals):
        super().__init__()
        self.report_id = report_id
        self.document = document
        self.endpoint = endpoint
        self.signals = signals

    def run(self):
        try:
            request = Request(
                self.endpoint,
                data=self.document.to_json().encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json", "User-Agent": "ZapZap-Report-Client/1"},
            )
            with urlopen(request, timeout=15, context=ssl.create_default_context()) as response:
                raw = response.read(128 * 1024)
                result = json.loads(raw.decode("utf-8")) if raw else {}
                if not 200 <= response.status < 300:
                    raise RuntimeError(f"service returned HTTP {response.status}")
            self.signals.succeeded.emit(self.report_id, result)
        except (HTTPError, URLError, OSError, ValueError, RuntimeError) as error:
            self.signals.failed.emit(self.report_id, str(error))


class ReportSubmitter(QObject):
    """Transmit only a document covered by a fresh explicit-consent capability."""

    succeeded = pyqtSignal(str, object)
    failed = pyqtSignal(str, str)

    def __init__(self, endpoint: str = __report_api__, parent=None, thread_pool=None):
        super().__init__(parent)
        parts = urlsplit(endpoint)
        if parts.scheme != "https" or not parts.netloc:
            raise ValueError("report endpoint must be HTTPS")
        self.endpoint = endpoint
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self._signals = _SubmissionSignals(self)
        self._signals.succeeded.connect(self.succeeded.emit)
        self._signals.failed.connect(self.failed.emit)

    def submit(self, report_id: str, document: ReportDocument, consent: ExplicitSubmissionConsent):
        consent.consume(document)
        task = _SubmissionTask(report_id, document, self.endpoint, self._signals)
        self.thread_pool.start(task)
