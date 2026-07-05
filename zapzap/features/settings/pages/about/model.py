"""Model for About page static metadata."""

from __future__ import annotations

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR

from zapzap import __appname__, __bugreport__, __donationPage__, __version__, __website__
from zapzap.core.environment.environment_detector import EnvironmentDetector


class AboutSettingsModel:
    """Provides application, build, and project-link metadata."""

    @property
    def app_name(self) -> str:
        return __appname__

    @property
    def version_text(self) -> str:
        return __version__

    @property
    def qt_version_text(self) -> str:
        return f"Qt:{QT_VERSION_STR} - PyQt:{PYQT_VERSION_STR}"

    @property
    def build_information(self):
        return {
            "channel": EnvironmentDetector.CHANNEL,
            "provider": EnvironmentDetector.PROVIDER,
            "packaging": EnvironmentDetector.PACKAGING,
            "repository": EnvironmentDetector.BUILD_REPOSITORY,
        }

    @property
    def project_links(self):
        return {
            "website": __website__,
            "bug_report": __bugreport__,
            "donation": __donationPage__,
        }
