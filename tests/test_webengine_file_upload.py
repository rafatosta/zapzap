"""Regression tests for WebEngine file selection and Flatpak file drops."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PyQt6.QtCore import QMimeData, QPointF, QStandardPaths, Qt, QUrl
from PyQt6.QtGui import QDropEvent
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QFileDialog

from qt_test_case import QtTestCase
from zapzap.features.browser.web import page_controller as page_controller_module
from zapzap.features.browser.web import web_view as web_view_module
from zapzap.features.browser.web.page_controller import (
    PageController,
    _choose_files_with_system_dialog,
)
from zapzap.features.browser.web.web_view import (
    _drop_paths_need_portal_confirmation,
    _prepare_portal_drop_event,
)
from zapzap.core.environment.setup_manager import SetupManager


class WebEngineFileChooserTests(unittest.TestCase):

    def setUp(self):
        self.parent = object()

    def test_single_file_chooser_shows_all_files(self):
        mode = QWebEnginePage.FileSelectionMode.FileSelectOpen
        with (
            patch.object(
                page_controller_module,
                "SystemSettings",
                return_value=SimpleNamespace(dont_use_native_dialog=False),
            ),
            patch.object(
                QFileDialog,
                "getOpenFileName",
                return_value=("/mnt/media/report.pdf", ""),
            ) as open_file,
        ):
            selected = _choose_files_with_system_dialog(
                self.parent, mode, ["/mnt/media/previous.txt"]
            )

        self.assertEqual(selected, ["/mnt/media/report.pdf"])
        open_file.assert_called_once_with(
            self.parent,
            "",
            "/mnt/media",
            "",
            QFileDialog.Option(0),
        )

    def test_multiple_files_respect_non_native_dialog_preference(self):
        mode = QWebEnginePage.FileSelectionMode.FileSelectOpenMultiple
        selected_paths = ["/mnt/media/one.pdf", "/mnt/media/two.pdf"]
        with (
            patch.object(
                page_controller_module,
                "SystemSettings",
                return_value=SimpleNamespace(dont_use_native_dialog=True),
            ),
            patch.object(
                QFileDialog,
                "getOpenFileNames",
                return_value=(selected_paths, ""),
            ) as open_files,
        ):
            selected = _choose_files_with_system_dialog(
                self.parent, mode
            )

        self.assertEqual(selected, selected_paths)
        open_files.assert_called_once_with(
            self.parent,
            "",
            "",
            "",
            QFileDialog.Option.DontUseNativeDialog,
        )

    def test_upload_folder_and_save_modes(self):
        settings = patch.object(
            page_controller_module,
            "SystemSettings",
            return_value=SimpleNamespace(dont_use_native_dialog=False),
        )
        with (
            settings,
            patch.object(
                QFileDialog,
                "getExistingDirectory",
                return_value="/mnt/media/folder",
            ) as choose_folder,
        ):
            folder = _choose_files_with_system_dialog(
                self.parent,
                QWebEnginePage.FileSelectionMode.FileSelectUploadFolder,
            )

        choose_folder.assert_called_once_with(
            self.parent, "", "", options=QFileDialog.Option(0)
        )
        self.assertEqual(folder, ["/mnt/media/folder"])

        with (
            patch.object(
                page_controller_module,
                "SystemSettings",
                return_value=SimpleNamespace(dont_use_native_dialog=False),
            ),
            patch.object(
                QFileDialog,
                "getSaveFileName",
                return_value=("", ""),
            ) as save_file,
        ):
            selected = _choose_files_with_system_dialog(
                self.parent,
                QWebEnginePage.FileSelectionMode.FileSelectSave,
            )

        save_file.assert_called_once_with(
            self.parent, "", "", "", QFileDialog.Option(0)
        )
        self.assertEqual(selected, [])

    def test_page_controller_uses_system_dialog_for_webengine_requests(self):
        mode = QWebEnginePage.FileSelectionMode.FileSelectOpen
        fake_page = SimpleNamespace(view=lambda: self.parent)
        with patch.object(
            page_controller_module,
            "_choose_files_with_system_dialog",
            return_value=["/mnt/media/document.pdf"],
        ) as choose_files:
            result = PageController.chooseFiles(
                fake_page, mode, [], ["application/pdf"]
            )

        self.assertEqual(result, ["/mnt/media/document.pdf"])
        choose_files.assert_called_once_with(self.parent, mode, ())


class FlatpakFileDropTests(QtTestCase):

    def setUp(self):
        super().setUp()
        self.parent = object()

    @staticmethod
    def _standard_locations():
        locations = QStandardPaths.StandardLocation
        return {
            locations.DocumentsLocation: "/home/test/Documents",
            locations.PicturesLocation: "/home/test/Pictures",
            locations.DownloadLocation: "/home/test/Downloads",
            locations.TempLocation: "/tmp",
        }

    def _patch_flatpak_paths(self):
        return (
            patch.object(SetupManager, "_is_flatpak", True),
            patch.object(
                web_view_module.QStandardPaths,
                "writableLocation",
                side_effect=self._standard_locations().get,
            ),
        )

    def test_only_external_flatpak_paths_require_confirmation(self):
        flatpak, locations = self._patch_flatpak_paths()
        with flatpak, locations:
            self.assertFalse(
                _drop_paths_need_portal_confirmation(
                    ["/home/test/Downloads/document.pdf"]
                )
            )
            self.assertTrue(
                _drop_paths_need_portal_confirmation(
                    ["/run/media/test/backup/document.pdf"]
                )
            )

    def test_external_drop_is_rewritten_with_portal_selected_files(self):
        original_path = "/run/media/test/backup/document.pdf"
        granted_path = "/run/user/1000/doc/abcd/document.pdf"
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(original_path)])
        event = QDropEvent(
            QPointF(10, 10),
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        flatpak, locations = self._patch_flatpak_paths()
        with (
            flatpak,
            locations,
            patch.object(
                web_view_module,
                "_choose_files_with_system_dialog",
                return_value=[granted_path],
            ) as choose_files,
        ):
            forwarded_event, mime_owner = _prepare_portal_drop_event(
                self.parent, event
            )

        choose_files.assert_called_once_with(
            self.parent,
            QWebEnginePage.FileSelectionMode.FileSelectOpenMultiple,
            [original_path],
        )
        self.assertIsNotNone(mime_owner)
        self.assertEqual(
            [url.toLocalFile() for url in forwarded_event.mimeData().urls()],
            [granted_path],
        )

    def test_drop_from_shared_flatpak_folder_keeps_native_webengine_path(self):
        mime_data = QMimeData()
        mime_data.setUrls([
            QUrl.fromLocalFile("/home/test/Downloads/document.pdf")
        ])
        event = QDropEvent(
            QPointF(10, 10),
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        flatpak, locations = self._patch_flatpak_paths()
        with (
            flatpak,
            locations,
            patch.object(
                web_view_module,
                "_choose_files_with_system_dialog",
            ) as choose_files,
        ):
            forwarded_event, mime_owner = _prepare_portal_drop_event(
                self.parent, event
            )

        choose_files.assert_not_called()
        self.assertIs(forwarded_event, event)
        self.assertIsNone(mime_owner)

    def test_cancelled_portal_confirmation_does_not_forward_drop(self):
        mime_data = QMimeData()
        mime_data.setUrls([
            QUrl.fromLocalFile("/run/media/test/backup/document.pdf")
        ])
        event = QDropEvent(
            QPointF(10, 10),
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        flatpak, locations = self._patch_flatpak_paths()
        with (
            flatpak,
            locations,
            patch.object(
                web_view_module,
                "_choose_files_with_system_dialog",
                return_value=[],
            ) as choose_files,
        ):
            forwarded_event, mime_owner = _prepare_portal_drop_event(
                self.parent, event
            )

        choose_files.assert_called_once()
        self.assertIsNone(forwarded_event)
        self.assertIsNone(mime_owner)
