"""One-time automatic provisioning of the system-locale dictionary."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.features.dictionaries.dictionary_service import DictionaryService


logger = logging.getLogger(__name__)


class SystemDictionaryProvisioner(QObject):
    """Install only the system dictionary when no package catalog is usable."""

    dictionary_installed = pyqtSignal(str)
    _PROVISIONED_LOCALE_KEY = "system/spellCheckProvisionedLocale"

    def __init__(self, parent=None, *, service=None):
        super().__init__(parent)
        self.service = service
        self._service_connected = False
        self._system_locale = ""
        self._entry = None

    def _ensure_service(self):
        if self.service is None:
            self.service = DictionaryService(self)
        if self._service_connected:
            return
        self.service.catalog_loaded.connect(self._catalog_loaded)
        self.service.catalog_failed.connect(self._catalog_failed)
        self.service.download_finished.connect(self._download_finished)
        self._service_connected = True

    def start(self) -> bool:
        """Start provisioning if the system locale has not been handled yet."""
        if not DictionariesManager.is_management_available():
            return False

        self._system_locale = DictionariesManager.get_system_language()
        if not self._system_locale:
            return False
        if SettingsManager.get(self._PROVISIONED_LOCALE_KEY, "") == self._system_locale:
            return False

        installed = DictionariesManager.list()
        if DictionariesManager.system_language_candidate(installed):
            SettingsManager.set(self._PROVISIONED_LOCALE_KEY, self._system_locale)
            return False

        self._ensure_service()
        self.service.fetch_catalog()
        return True

    def _catalog_loaded(self, snapshot) -> None:
        code = DictionariesManager.system_language_candidate(
            [entry.code for entry in snapshot.entries]
        )
        if not code:
            logger.info(
                "No dictionary is available for the system locale %s",
                self._system_locale,
            )
            return
        if code in DictionariesManager.list():
            SettingsManager.set(self._PROVISIONED_LOCALE_KEY, self._system_locale)
            return
        self._entry = next(entry for entry in snapshot.entries if entry.code == code)
        self.service.install(self._entry)

    def _catalog_failed(self, detail: str, _using_cache: bool) -> None:
        logger.warning("Could not provision the system dictionary: %s", detail)

    def _download_finished(self, code: str, result) -> None:
        if self._entry is None or code != self._entry.code:
            return
        entry = self._entry
        self._entry = None
        if not result.success:
            logger.warning(
                "Could not install the system dictionary %s: %s",
                code,
                result.detail or result.error,
            )
            return
        try:
            DictionariesManager.record_install(
                code,
                {
                    "source": entry.source,
                    "source_revision": entry.source_revision,
                    "qt_version": entry.qt_version,
                    "sha256": entry.sha256,
                    "git_sha": entry.git_sha,
                    "size": entry.size,
                },
            )
        except (OSError, ValueError) as error:
            try:
                (Path(DictionariesManager.get_path()) / entry.filename).unlink()
            except OSError:
                logger.warning(
                    "Could not roll back the system dictionary after metadata failure"
                )
            logger.warning("Could not record the system dictionary: %s", error)
            return
        SettingsManager.set(self._PROVISIONED_LOCALE_KEY, self._system_locale)
        self.dictionary_installed.emit(code)

    def close(self) -> None:
        if self.service is not None:
            self.service.close()
