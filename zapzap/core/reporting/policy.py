"""Central policy for errors eligible for locally prepared reports."""

from enum import Enum


class ErrorSeverity(str, Enum):
    WARNING = "warning"
    RECOVERABLE = "recoverable_error"
    CRITICAL = "critical_error"
    FATAL = "fatal_crash"


class ReportPolicy:
    """Keep ordinary warnings and handled errors out of crash prompts."""

    @staticmethod
    def classify(*, unhandled: bool, process_fatal: bool = False) -> ErrorSeverity:
        if process_fatal:
            return ErrorSeverity.FATAL
        if unhandled:
            return ErrorSeverity.CRITICAL
        return ErrorSeverity.RECOVERABLE

    @staticmethod
    def should_prepare(severity: ErrorSeverity) -> bool:
        return severity in {ErrorSeverity.CRITICAL, ErrorSeverity.FATAL}
