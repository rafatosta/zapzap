"""UI orchestration for the reusable dictionary manager dialog."""

from __future__ import annotations

from gettext import gettext as _
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget

from zapzap.features.dictionaries.dictionaries_manager import (
    DictionariesManager,
    DictionaryError,
)
from zapzap.features.dictionaries.dictionary_service import DictionaryService
from zapzap.features.dictionaries.spellcheck_language_picker import (
    open_spellcheck_language_picker,
)
from zapzap.ui.components import DictionaryManagerDialog


logger = logging.getLogger(__name__)


def _update_browser_spellcheck() -> None:
    app = QApplication.instance()
    window = getattr(app, "getWindow", lambda: None)() if app else None
    browser = getattr(window, "browser", None)
    update = getattr(browser, "update_spellcheck", None)
    if callable(update):
        update()


def open_dictionary_manager(
    parent: QWidget | None = None,
    *,
    on_changed=None,
) -> bool:
    """Open one manager; network activity starts only after this call."""
    if not DictionariesManager.is_management_available():
        return False
    dialog = DictionaryManagerDialog(parent)
    service = DictionaryService(dialog)
    catalog_snapshot = None

    def refresh_states():
        states = DictionariesManager.states(
            catalog_snapshot.entries if catalog_snapshot else ()
        )
        if catalog_snapshot:
            dialog.set_catalog(catalog_snapshot, states)
        else:
            dialog.set_installed_only(states)

    def notify_changed():
        (on_changed or _update_browser_spellcheck)()
        refresh_states()

    def catalog_loaded(snapshot):
        nonlocal catalog_snapshot
        catalog_snapshot = snapshot
        refresh_states()

    def catalog_failed(detail, using_cache):
        dialog.set_catalog_error(detail, using_cache)
        if not using_cache:
            refresh_states()

    def install(code):
        entry = dialog.catalog_entry(code)
        if entry is None:
            return
        dialog.set_download_busy(code, True)
        service.install(entry)

    def download_finished(code, result):
        dialog.set_download_busy(code, False)
        if result.success:
            entry = dialog.catalog_entry(code)
            if entry is not None:
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
                            "Could not roll back dictionary after metadata failure"
                        )
                    result = type(result)(
                        False,
                        code,
                        DictionaryError.PERMISSION,
                        str(error),
                    )
            if result.success:
                notify_changed()
        dialog.set_operation_result(result)

    def remove(code):
        answer = QMessageBox.question(
            dialog,
            _("Remove dictionary"),
            _("Remove the dictionary {code}?").format(code=code),
            QMessageBox.StandardButton.Remove | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Remove:
            return
        result = DictionariesManager.remove(code)
        if result.error == DictionaryError.LAST_ACTIVE:
            answer = QMessageBox.warning(
                dialog,
                _("Disable spell checker and remove"),
                _(
                    "This is the last active dictionary. Disable the spell "
                    "checker and remove {code}?"
                ).format(code=code),
                QMessageBox.StandardButton.Remove | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer == QMessageBox.StandardButton.Remove:
                result = DictionariesManager.remove(code, disable_if_last=True)
        dialog.set_operation_result(result)
        if result.success:
            notify_changed()

    def import_files(paths):
        results = []
        for path in paths:
            result = DictionariesManager.import_file(path)
            if result.error == DictionaryError.CONFLICT:
                answer = QMessageBox.question(
                    dialog,
                    _("Replace dictionary"),
                    _(
                        "A different dictionary named {code} is installed. "
                        "Replace it?"
                    ).format(code=result.code),
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel,
                )
                if answer == QMessageBox.StandardButton.Yes:
                    result = DictionariesManager.import_file(path, replace=True)
            results.append(result)
        failures = [result for result in results if not result.success]
        successes = [result for result in results if result.success]
        result = failures[0] if failures else results[-1] if results else None
        if result is not None:
            dialog.set_operation_result(result)
        if successes:
            notify_changed()
        else:
            refresh_states()

    def import_directory(path):
        results = DictionariesManager.import_directory(path)
        for index, result in enumerate(results):
            if result.error != DictionaryError.CONFLICT:
                continue
            answer = QMessageBox.question(
                dialog,
                _("Replace dictionary"),
                _(
                    "A different dictionary named {code} is installed. Replace it?"
                ).format(code=result.code),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer == QMessageBox.StandardButton.Yes:
                results[index] = DictionariesManager.import_file(
                    Path(path) / f"{result.code}.bdic",
                    replace=True,
                )
        failures = [result for result in results if not result.success]
        successes = [result for result in results if result.success]
        result = failures[0] if failures else results[-1] if results else None
        if result is not None:
            dialog.set_operation_result(result)
        if successes:
            notify_changed()
        else:
            refresh_states()

    def choose_active_languages():
        if open_spellcheck_language_picker(
            dialog,
            on_applied=notify_changed,
            on_manage=lambda: (dialog.show(), dialog.raise_()),
        ):
            refresh_states()

    service.catalog_loaded.connect(catalog_loaded)
    service.catalog_failed.connect(catalog_failed)
    service.download_progress.connect(dialog.set_download_progress)
    service.download_finished.connect(download_finished)
    dialog.refresh_requested.connect(lambda force: service.fetch_catalog(force=force))
    dialog.install_requested.connect(install)
    dialog.cancel_requested.connect(service.cancel)
    dialog.remove_requested.connect(remove)
    dialog.import_files_requested.connect(import_files)
    dialog.import_directory_requested.connect(import_directory)
    dialog.active_languages_requested.connect(choose_active_languages)
    dialog.finished.connect(lambda _result: service.close())

    dialog.set_installed_only(DictionariesManager.states(), loading=True)
    service.fetch_catalog()
    dialog.exec()
    return True
