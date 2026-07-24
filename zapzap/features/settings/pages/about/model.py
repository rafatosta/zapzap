"""Model for About page metadata and safe diagnostic information."""

from __future__ import annotations

import os
import platform

from gettext import gettext as _

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QSysInfo

from zapzap import (
    __appname__,
    __author__,
    __bugreport__,
    __donationPage__,
    __licence__,
    __version__,
    __website__,
)
from zapzap.core.environment.environment_detector import EnvironmentDetector


class AboutSettingsModel:
    """Provides application, build, project, and diagnostic metadata."""

    @property
    def app_name(self) -> str:
        return __appname__

    @property
    def version_text(self) -> str:
        return __version__

    @property
    def project_links(self):
        return {
            "website": __website__,
            "bug_report": __bugreport__,
            "donation": __donationPage__,
        }

    @property
    def license_name(self) -> str:
        return __licence__

    @property
    def author_name(self) -> str:
        return __author__

    @staticmethod
    def _is_available(value) -> bool:
        text = str(value or "").strip()
        return bool(text) and text.casefold() not in {
            "unknown",
            _("Unknown").casefold(),
        }

    @property
    def technical_details(self):
        details = [
            (_("Version"), self.version_text),
            ("Qt", QT_VERSION_STR),
            ("PyQt", PYQT_VERSION_STR),
        ]
        optional_details = (
            (_("Channel"), EnvironmentDetector.CHANNEL),
            (_("Packaging"), EnvironmentDetector.PACKAGING),
            (_("Provider"), EnvironmentDetector.PROVIDER),
            (_("Repository"), EnvironmentDetector.BUILD_REPOSITORY),
        )
        details.extend(
            (label, str(value))
            for label, value in optional_details
            if self._is_available(value)
        )
        return details

    @property
    def system_information(self) -> str:
        """Return useful non-personal diagnostics, omitting unavailable values."""

        values = [
            (None, f"{self.app_name} {self.version_text}"),
            ("Qt", QT_VERSION_STR),
            ("PyQt", PYQT_VERSION_STR),
            ("Python", platform.python_version()),
            (_("System"), QSysInfo.prettyProductName()),
            (_("Session"), os.environ.get("XDG_SESSION_TYPE")),
            (_("Packaging"), EnvironmentDetector.PACKAGING),
            (_("Channel"), EnvironmentDetector.CHANNEL),
        ]

        lines = []
        for label, value in values:
            if not self._is_available(value):
                continue
            lines.append(str(value) if label is None else f"{label}: {value}")
        return "\n".join(lines)
