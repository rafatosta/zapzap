"""Regression tests for explicit Qt desktop-media source selection."""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PyQt6 import sip
from PyQt6.QtCore import (
    QItemSelectionModel,
    QModelIndex,
    QPersistentModelIndex,
    QObject,
    QStringListModel,
    Qt,
)
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QDialog, QWidget

from qt_test_case import QtTestCase
from zapzap.features.browser.web.page_controller import (
    DesktopMediaRequestCoordinator,
    PageController,
    connect_desktop_media_requested,
)
from zapzap.features.permissions.permissions_manager import PermissionsManager
from zapzap.ui.components.desktop_media_picker_dialog import (
    DesktopMediaKind,
    DesktopMediaPickerDialog,
    DesktopMediaSelection,
)


def select_index(view, index):
    view.selectionModel().select(
        index,
        QItemSelectionModel.SelectionFlag.ClearAndSelect,
    )


def delete_qobject(obj):
    obj.deleteLater()


class DesktopMediaPickerTests(QtTestCase):

    def make_dialog(self, screens=(), windows=()):
        dialog = DesktopMediaPickerDialog(
            QStringListModel(list(screens)),
            QStringListModel(list(windows)),
        )
        self.addCleanup(delete_qobject, dialog)
        return dialog

    def test_sources_are_separate_and_display_original_model_text(self):
        dialog = self.make_dialog(
            screens=("Display 1", "Display 2"),
            windows=("Window 1",),
        )

        self.assertIs(dialog.screen_list.model(), dialog._models[DesktopMediaKind.SCREEN])
        self.assertIs(dialog.window_list.model(), dialog._models[DesktopMediaKind.WINDOW])
        self.assertEqual(
            dialog.screen_list.model().index(1, 0).data(Qt.ItemDataRole.DisplayRole),
            "Display 2",
        )
        self.assertEqual(dialog.source_tabs.tabText(0), "Screens")
        self.assertEqual(dialog.source_tabs.tabText(1), "Windows")

    def test_single_source_is_not_selected_automatically(self):
        dialog = self.make_dialog(screens=("Only display",))

        self.assertEqual(dialog.screen_list.selectedIndexes(), [])
        self.assertIsNone(dialog.selection)
        self.assertFalse(dialog.share_button.isEnabled())
        dialog._accept_if_valid()
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)

    def test_activation_only_accepts_an_explicit_valid_selection(self):
        dialog = self.make_dialog(screens=("Display",))
        model = dialog.screen_list.model()

        dialog.screen_list.activated.emit(QModelIndex())
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)

        index = model.index(0, 0)
        select_index(dialog.screen_list, index)
        dialog.screen_list.activated.emit(index)
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)

    def test_explicit_screen_selection_returns_original_model_index(self):
        dialog = self.make_dialog(screens=("Display",), windows=("Window",))
        model = dialog.screen_list.model()
        select_index(dialog.screen_list, model.index(0, 0))

        self.assertTrue(dialog.share_button.isEnabled())
        dialog._accept_if_valid()

        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(dialog.selection.kind, DesktopMediaKind.SCREEN)
        self.assertIs(dialog.selection.index.model(), model)

    def test_explicit_window_selection_clears_screen_selection(self):
        dialog = self.make_dialog(screens=("Display",), windows=("Window",))
        select_index(dialog.screen_list, dialog.screen_list.model().index(0, 0))
        select_index(dialog.window_list, dialog.window_list.model().index(0, 0))

        self.assertEqual(dialog.screen_list.selectedIndexes(), [])
        dialog._accept_if_valid()

        self.assertEqual(dialog.selection.kind, DesktopMediaKind.WINDOW)
        self.assertIs(dialog.selection.index.model(), dialog.window_list.model())

    def test_cancel_button_escape_and_close_are_rejections(self):
        cancel_dialog = self.make_dialog(screens=("Display",))
        cancel_dialog.cancel_button.click()
        self.assertEqual(cancel_dialog.result(), QDialog.DialogCode.Rejected)
        self.assertEqual(cancel_dialog.rejection_reason, "user_cancelled")

        escape_dialog = self.make_dialog(screens=("Display",))
        event = Mock()
        event.key.return_value = Qt.Key.Key_Escape
        escape_dialog.keyPressEvent(event)
        event.accept.assert_called_once_with()
        self.assertEqual(escape_dialog.result(), QDialog.DialogCode.Rejected)
        self.assertEqual(escape_dialog.rejection_reason, "user_cancelled")

        close_dialog = self.make_dialog(screens=("Display",))
        close_dialog.close()
        self.assertEqual(close_dialog.result(), QDialog.DialogCode.Rejected)
        self.assertEqual(close_dialog.rejection_reason, "dialog_closed")

    def test_empty_categories_and_dynamic_insertion_are_presented(self):
        dialog = self.make_dialog()
        screens = dialog.screen_list.model()

        self.assertIs(dialog._screen_stack.currentWidget(), dialog.screen_empty_label)
        self.assertIs(dialog._window_stack.currentWidget(), dialog.window_empty_label)
        screens.insertRow(0)
        screens.setData(screens.index(0, 0), "New display")

        self.assertIs(dialog._screen_stack.currentWidget(), dialog.screen_list)
        self.assertEqual(screens.index(0, 0).data(), "New display")
        self.assertEqual(dialog.screen_list.selectedIndexes(), [])
        self.assertFalse(dialog.share_button.isEnabled())

    def test_removing_selected_source_invalidates_and_rejects(self):
        dialog = self.make_dialog(screens=("Display", "Other"))
        model = dialog.screen_list.model()
        select_index(dialog.screen_list, model.index(0, 0))

        model.removeRow(0)

        self.assertFalse(dialog.share_button.isEnabled())
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)
        self.assertEqual(dialog.rejection_reason, "invalid_selection")
        self.assertIsNone(dialog.selection)

    def test_accessibility_focus_order_and_webengine_independence(self):
        dialog = self.make_dialog(screens=("Display",), windows=("Window",))

        for widget in (
            dialog.source_tabs,
            dialog.screen_list,
            dialog.window_list,
            dialog.cancel_button,
            dialog.share_button,
            dialog.close_button,
        ):
            self.assertTrue(widget.accessibleName())
        self.assertTrue(dialog.screen_list.accessibleDescription())
        focus_chain = []
        widget = dialog.source_tabs
        for _index in range(100):
            widget = widget.nextInFocusChain()
            focus_chain.append(widget)
        for expected in (
            dialog.screen_list,
            dialog.window_list,
            dialog.cancel_button,
            dialog.share_button,
            dialog.close_button,
        ):
            self.assertIn(expected, focus_chain)
        self.assertLess(
            focus_chain.index(dialog.cancel_button),
            focus_chain.index(dialog.share_button),
        )
        self.assertNotIn("QtWebEngine", inspect.getsource(
            inspect.getmodule(DesktopMediaPickerDialog)
        ))


class FakeRequest:

    def __init__(self, screens=None, windows=None):
        self.screens = screens
        self.windows = windows
        self.screen_indexes = []
        self.window_indexes = []
        self.cancel_count = 0

    def screensModel(self):
        return self.screens

    def windowsModel(self):
        return self.windows

    def selectScreen(self, index):
        self.screen_indexes.append(QModelIndex(index))

    def selectWindow(self, index):
        self.window_indexes.append(QModelIndex(index))

    def cancel(self):
        self.cancel_count += 1


class FakeDialog:

    def __init__(self, result, selection=None, on_exec=None, reason="user_cancelled"):
        self._result = result
        self.selection = selection
        self.rejection_reason = reason
        self.on_exec = on_exec
        self.deleted = False
        self.reject_count = 0

    def exec(self):
        if self.on_exec is not None:
            self.on_exec()
        return self._result

    def reject(self):
        self.reject_count += 1

    def deleteLater(self):
        self.deleted = True


class DesktopMediaCoordinatorTests(QtTestCase):

    def setUp(self):
        self.parent = QWidget()
        self.addCleanup(delete_qobject, self.parent)

    def coordinator_for(self, dialog):
        return DesktopMediaRequestCoordinator(
            lambda: self.parent,
            lambda _screens, _windows, _parent: dialog,
        )

    @staticmethod
    def selection(kind, model, row=0):
        return DesktopMediaSelection(
            kind,
            QPersistentModelIndex(model.index(row, 0)),
        )

    def test_signal_connection_is_capability_checked(self):
        signal = SimpleNamespace(connect=Mock())
        page = SimpleNamespace(desktopMediaRequested=signal)
        handler = Mock()

        self.assertTrue(connect_desktop_media_requested(page, handler))
        signal.connect.assert_called_once_with(handler)
        self.assertFalse(connect_desktop_media_requested(object(), handler))

    def test_screen_selection_resolves_only_with_select_screen(self):
        screens = QStringListModel(["Private screen title"])
        request = FakeRequest(screens, QStringListModel())
        dialog = FakeDialog(
            QDialog.DialogCode.Accepted,
            self.selection(DesktopMediaKind.SCREEN, screens),
        )
        coordinator = self.coordinator_for(dialog)

        with self.assertLogs(
            "zapzap.features.browser.web.page_controller", level="INFO"
        ) as captured:
            coordinator.handle(request)

        self.assertEqual(len(request.screen_indexes), 1)
        self.assertIs(request.screen_indexes[0].model(), screens)
        self.assertEqual(request.window_indexes, [])
        self.assertEqual(request.cancel_count, 0)
        self.assertFalse(coordinator.has_active_request)
        self.assertNotIn("Private screen title", "\n".join(captured.output))

    def test_window_selection_resolves_only_with_select_window(self):
        windows = QStringListModel(["Private window title"])
        request = FakeRequest(QStringListModel(), windows)
        dialog = FakeDialog(
            QDialog.DialogCode.Accepted,
            self.selection(DesktopMediaKind.WINDOW, windows),
        )
        coordinator = self.coordinator_for(dialog)

        coordinator.handle(request)

        self.assertEqual(request.screen_indexes, [])
        self.assertEqual(len(request.window_indexes), 1)
        self.assertIs(request.window_indexes[0].model(), windows)
        self.assertEqual(request.cancel_count, 0)

    def test_rejection_and_missing_selection_cancel_once(self):
        for result, selection in (
            (QDialog.DialogCode.Rejected, None),
            (QDialog.DialogCode.Accepted, None),
        ):
            with self.subTest(result=result):
                request = FakeRequest(QStringListModel(["Display"]), QStringListModel())
                coordinator = self.coordinator_for(FakeDialog(result, selection))
                coordinator.handle(request)
                self.assertEqual(request.cancel_count, 1)
                self.assertEqual(request.screen_indexes, [])
                self.assertEqual(request.window_indexes, [])
                self.assertFalse(coordinator.has_active_request)

    def test_absent_models_cancel_without_opening_a_dialog(self):
        request = FakeRequest()
        factory = Mock()
        coordinator = DesktopMediaRequestCoordinator(
            lambda: self.parent,
            factory,
        )

        coordinator.handle(request)

        self.assertEqual(request.cancel_count, 1)
        factory.assert_not_called()
        self.assertFalse(coordinator.has_active_request)

    def test_wrong_model_or_invalid_index_cancels(self):
        screens = QStringListModel(["Display"])
        other = QStringListModel(["Other"])
        for selection in (
            self.selection(DesktopMediaKind.SCREEN, other),
            DesktopMediaSelection(
                DesktopMediaKind.SCREEN,
                QPersistentModelIndex(),
            ),
        ):
            with self.subTest(selection=selection):
                request = FakeRequest(screens, QStringListModel())
                coordinator = self.coordinator_for(
                    FakeDialog(QDialog.DialogCode.Accepted, selection)
                )
                coordinator.handle(request)
                self.assertEqual(request.cancel_count, 1)
                self.assertEqual(request.screen_indexes, [])

    def test_concurrent_request_is_cancelled_without_replacing_active(self):
        screens = QStringListModel(["Display"])
        first = FakeRequest(screens, QStringListModel())
        second = FakeRequest(screens, QStringListModel())
        coordinator = None

        def submit_second():
            coordinator.handle(second)

        dialog = FakeDialog(
            QDialog.DialogCode.Rejected,
            on_exec=submit_second,
        )
        coordinator = self.coordinator_for(dialog)
        coordinator.handle(first)

        self.assertEqual(first.cancel_count, 1)
        self.assertEqual(second.cancel_count, 1)
        self.assertFalse(coordinator.has_active_request)

    def test_page_destruction_cancels_active_and_closes_picker(self):
        screens = QStringListModel(["Display"])
        request = FakeRequest(screens, QStringListModel())
        coordinator = None
        page_owner = QObject()
        dialog = FakeDialog(
            QDialog.DialogCode.Rejected,
            on_exec=lambda: sip.delete(page_owner),
        )
        coordinator = self.coordinator_for(dialog)
        page_owner.destroyed.connect(coordinator.page_destroyed)

        coordinator.handle(request)

        self.assertEqual(request.cancel_count, 1)
        self.assertEqual(dialog.reject_count, 1)
        self.assertFalse(coordinator.has_active_request)

    def test_model_query_and_selection_failures_cancel_and_clear_state(self):
        query_failure = FakeRequest()
        query_failure.screensModel = Mock(side_effect=RuntimeError("destroyed"))
        coordinator = self.coordinator_for(
            FakeDialog(QDialog.DialogCode.Rejected)
        )
        with self.assertLogs(
            "zapzap.features.browser.web.page_controller", level="ERROR"
        ):
            coordinator.handle(query_failure)
        self.assertEqual(query_failure.cancel_count, 1)

        screens = QStringListModel(["Display"])
        selection_failure = FakeRequest(screens, QStringListModel())
        selection_failure.selectScreen = Mock(side_effect=RuntimeError("destroyed"))
        dialog = FakeDialog(
            QDialog.DialogCode.Accepted,
            self.selection(DesktopMediaKind.SCREEN, screens),
        )
        coordinator = self.coordinator_for(dialog)
        with self.assertLogs(
            "zapzap.features.browser.web.page_controller", level="ERROR"
        ):
            coordinator.handle(selection_failure)
        selection_failure.selectScreen.assert_called_once()
        self.assertEqual(selection_failure.cancel_count, 1)
        self.assertFalse(coordinator.has_active_request)

    def test_later_request_works_after_previous_cancellation(self):
        screens = QStringListModel(["Display"])
        first = FakeRequest(screens, QStringListModel())
        second = FakeRequest(screens, QStringListModel())
        dialogs = iter((
            FakeDialog(QDialog.DialogCode.Rejected),
            FakeDialog(
                QDialog.DialogCode.Accepted,
                self.selection(DesktopMediaKind.SCREEN, screens),
            ),
        ))
        coordinator = DesktopMediaRequestCoordinator(
            lambda: self.parent,
            lambda _screens, _windows, _parent: next(dialogs),
        )

        coordinator.handle(first)
        coordinator.handle(second)

        self.assertEqual(first.cancel_count, 1)
        self.assertEqual(len(second.screen_indexes), 1)
        self.assertEqual(second.cancel_count, 0)

    def test_existing_desktop_permission_flow_remains_independent(self):
        fake_page = SimpleNamespace(
            _granted_features=set(),
            setFeaturePermission=Mock(),
            parent=lambda: self.parent,
        )
        feature = QWebEnginePage.Feature.DesktopVideoCapture
        with (
            patch.object(PermissionsManager, "is_auto_grant_enabled", return_value=False),
            patch(
                "zapzap.features.browser.web.page_controller.AlertManager.question",
                return_value=True,
            ) as question,
        ):
            PageController._on_feature_permission_requested(
                fake_page,
                "origin",
                feature,
            )

        question.assert_called_once()
        fake_page.setFeaturePermission.assert_called_once_with(
            "origin",
            feature,
            QWebEnginePage.PermissionPolicy.PermissionGrantedByUser,
        )
        self.assertIn(feature, fake_page._granted_features)


if __name__ == "__main__":
    import unittest

    unittest.main()
