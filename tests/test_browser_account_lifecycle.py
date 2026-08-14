"""Regression tests for the browser's account runtime registry."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QMenu

from qt_test_case import QtTestCase
from zapzap.features.browser.shell.browser_controller import (
    AccountLifecycle,
    AccountRuntime,
    BrowserController,
)


class FakeSignal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self, *args):
        for callback in list(self.callbacks):
            callback(*args)


class FakeButton:
    def __init__(self, user, page_index):
        self.user = user
        self.page_index = page_index
        self.clicked = FakeSignal()
        self.customContextMenuRequested = FakeSignal()
        self.close = Mock()
        self.deleteLater = Mock()
        self.show = Mock()
        self.selected = Mock()
        self.unselected = Mock()
        self.update_notifications = Mock(side_effect=self._set_notifications)
        self.number_notifications = 0

    def _set_notifications(self, count):
        self.number_notifications = count

    def setObjectName(self, _name):
        pass

    def setContextMenuPolicy(self, _policy):
        pass


class FakePage:
    def __init__(self, user, position):
        self.user = user
        self.page_index = position
        self.update_button_signal = FakeSignal()
        self.disable_page = Mock()
        self.shutdown = Mock()
        self.remove_files = Mock()
        self.close = Mock()
        self.setParent = Mock()
        self.deleteLater = Mock()


class FakeWebViewFactory:
    def __init__(self):
        self.pages = []
        self.removed_user_ids = []

    def __call__(self, user, position):
        page = FakePage(user, position)
        self.pages.append(page)
        return page

    def remove_user_files(self, user_id):
        self.removed_user_ids.append(user_id)


class FailingThenWorkingFactory(FakeWebViewFactory):
    def __init__(self):
        super().__init__()
        self.failures = 1

    def __call__(self, user, position):
        if self.failures:
            self.failures -= 1
            raise RuntimeError("simulated profile failure")
        return super().__call__(user, position)


class FakeStack:
    def __init__(self):
        self.widgets = []
        self.current = None

    def addWidget(self, widget):
        self.widgets.append(widget)

    def removeWidget(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
        if self.current is widget:
            self.current = None

    def currentWidget(self):
        return self.current


class BrowserAccountLifecycleTest(QtTestCase):
    class Harness:
        _add_page = BrowserController._add_page
        _create_webview = BrowserController._create_webview
        _destroy_webview = BrowserController._destroy_webview
        _active_runtimes = BrowserController._active_runtimes
        _runtime_for_page = BrowserController._runtime_for_page
        _find_button_and_page_enabled = (
            BrowserController._find_button_and_page_enabled
        )
        _select_default_page = BrowserController._select_default_page
        _ensure_valid_selection = BrowserController._ensure_valid_selection
        disable_page = BrowserController.disable_page
        delete_page = BrowserController.delete_page
        close_pages = BrowserController.close_pages
        activate_account = BrowserController.activate_account
        update_account_notifications = (
            BrowserController.update_account_notifications
        )
        _update_total_notifications = (
            BrowserController._update_total_notifications
        )
        _update_runtime_notifications = (
            BrowserController._update_runtime_notifications
        )

    def setUp(self):
        self.factory = FakeWebViewFactory()
        self.controller = self.Harness()
        self.controller.page_count = 0
        self.controller._accounts = {}
        self.controller._webview_factory = self.factory
        self.controller._shutting_down = False
        self.controller._last_active_webview = None
        self.controller._grid_thumbnails = Mock()
        self.controller.pages = FakeStack()
        self.controller.page_buttons_layout = Mock()
        self.controller.grid_view = Mock()
        self.controller._select_default_page = Mock()
        self.controller._update_user_menu = Mock()
        self.controller._update_total_notifications = Mock()

    @staticmethod
    def _user(user_id, enabled):
        return SimpleNamespace(id=user_id, name=user_id, enable=enabled)

    def _add(self, user):
        with patch(
            "zapzap.features.browser.shell.browser_controller."
            "BrowserPageButton",
            FakeButton,
        ):
            return self.controller._add_page(user)

    def test_startup_creates_webviews_only_for_enabled_accounts(self):
        enabled = self._add(self._user("enabled", True))
        second_enabled = self._add(self._user("background", True))
        disabled = self._add(self._user("disabled", False))

        self.assertEqual(len(self.factory.pages), 2)
        self.assertIs(enabled.page, self.factory.pages[0])
        self.assertIs(second_enabled.page, self.factory.pages[1])
        self.assertEqual(enabled.state, AccountLifecycle.ACTIVE)
        self.assertIsNone(disabled.page)
        self.assertEqual(disabled.state, AccountLifecycle.DISABLED)

    def test_one_profile_failure_is_isolated_and_can_be_retried(self):
        self.controller._webview_factory = FailingThenWorkingFactory()

        with self.assertLogs(
            "zapzap.features.browser.shell.browser_controller",
            level="ERROR",
        ):
            runtime = self._add(self._user("recoverable", True))

        self.assertIsNone(runtime.page)
        self.assertEqual(runtime.state, AccountLifecycle.ERROR)
        self.assertIsNotNone(self.controller._create_webview(runtime))
        self.assertEqual(runtime.state, AccountLifecycle.ACTIVE)

    def test_disabling_a_failed_profile_clears_the_error_state(self):
        self.controller._webview_factory = FailingThenWorkingFactory()
        with self.assertLogs(
            "zapzap.features.browser.shell.browser_controller",
            level="ERROR",
        ):
            runtime = self._add(self._user("failed", True))

        runtime.user.enable = False
        self.controller.disable_page(runtime.user)

        self.assertEqual(runtime.state, AccountLifecycle.DISABLED)

    def test_disable_enable_cycles_create_and_destroy_one_instance_each(self):
        user = self._user("cycle", True)
        runtime = self._add(user)
        first = runtime.page

        user.enable = False
        self.controller.disable_page(user)
        self.controller.disable_page(user)
        self.assertIsNone(runtime.page)
        first.disable_page.assert_called_once_with()

        user.enable = True
        self.controller.disable_page(user)
        second = runtime.page
        self.controller.disable_page(user)

        self.assertIsNot(first, second)
        self.assertEqual(len(self.factory.pages), 2)
        self.assertIs(runtime.page, second)

    def test_delete_cleans_active_and_never_instantiated_accounts(self):
        active_user = self._user("active", True)
        disabled_user = self._user("disabled", False)
        active = self._add(active_user)
        disabled = self._add(disabled_user)
        active_page = active.page

        self.controller.delete_page(active_user)
        self.controller.delete_page(disabled_user)

        active_page.shutdown.assert_called_once_with()
        active_page.remove_files.assert_called_once_with()
        self.assertEqual(self.factory.removed_user_ids, ["disabled"])
        self.assertEqual(self.controller._accounts, {})

    def test_close_is_idempotent_and_does_not_retain_pages(self):
        runtime = self._add(self._user("closing", True))
        page = runtime.page

        self.controller.close_pages()
        self.controller.close_pages()

        page.shutdown.assert_called_once_with()
        self.assertEqual(self.controller._accounts, {})
        self.assertIsNone(self.controller._last_active_webview)

    def test_notification_callback_resolves_current_registry_entry(self):
        user = self._user("messages", True)
        first = self._add(user)
        old_page = first.page

        old_page.update_button_signal.emit(first.position, 4)
        first.button.update_notifications.assert_called_once_with(4)
        self.controller.delete_page(user)

        replacement = self._add(user)
        old_page.update_button_signal.emit(first.position, 8)
        replacement.page.update_button_signal.emit(replacement.position, 2)

        replacement.button.update_notifications.assert_called_once_with(2)

    def test_activation_uses_stable_id_and_rejects_removed_account(self):
        runtime = self._add(self._user("target", True))
        self.controller.switch_to_page = Mock(return_value=True)

        self.assertTrue(self.controller.activate_account("target"))
        self.controller.switch_to_page.assert_called_once_with(
            runtime.page, runtime.button
        )
        self.assertFalse(self.controller.activate_account("missing"))

    def test_total_notifications_excludes_disabled_runtime(self):
        first = self._add(self._user("first", True))
        second = self._add(self._user("second", True))
        first.button.number_notifications = 3
        second.button.number_notifications = 5
        self.controller._update_total_notifications = (
            lambda: BrowserController._update_total_notifications(
                self.controller
            )
        )

        with patch(
            "zapzap.features.browser.shell.browser_controller."
            "SysTrayManager.set_number_notifications"
        ) as set_total:
            second.user.enable = False
            self.controller.disable_page(second.user)

        set_total.assert_called_with(3)

    def test_deleting_current_account_selects_the_next_enabled_account(self):
        current = self._add(self._user("current", True))
        remaining = self._add(self._user("remaining", True))
        self.controller.pages.current = current.page
        self.controller.switch_to_page = Mock()
        self.controller._select_default_page = (
            lambda: BrowserController._select_default_page(self.controller)
        )

        self.controller.delete_page(current.user)

        self.controller.switch_to_page.assert_called_once_with(
            remaining.page, remaining.button
        )

    def test_first_enabled_account_is_selected_from_stable_registry_order(self):
        self._add(self._user("disabled", False))
        first_enabled = self._add(self._user("first-enabled", True))
        self._add(self._user("second-enabled", True))
        self.controller.switch_to_page = Mock()

        BrowserController._select_default_page(self.controller)

        self.controller.switch_to_page.assert_called_once_with(
            first_enabled.page, first_enabled.button
        )

    def test_deleting_last_active_account_selects_empty_grid(self):
        current = self._add(self._user("only", True))
        self.controller.pages.current = current.page
        self.controller.show_grid_view = Mock()
        self.controller._select_default_page = (
            lambda: BrowserController._select_default_page(self.controller)
        )

        self.controller.delete_page(current.user)

        self.controller.show_grid_view.assert_called_once_with()

    def test_deleting_non_current_account_preserves_current_selection(self):
        current = self._add(self._user("current", True))
        other = self._add(self._user("other", True))
        self.controller.pages.current = current.page

        self.controller.delete_page(other.user)

        self.controller._select_default_page.assert_not_called()
        self.assertIs(self.controller.pages.currentWidget(), current.page)

    def test_user_menu_shortcuts_are_contiguous_and_resolve_stable_ids(self):
        with patch.object(BrowserController, "_initialize"):
            browser = BrowserController()
        self.addCleanup(browser.deleteLater)
        browser.parent = SimpleNamespace(menuUsers=QMenu())
        browser.activate_account = Mock()
        users = (
            self._user("first", True),
            self._user("disabled", False),
            self._user("third", True),
        )
        browser._accounts = {
            user.id: AccountRuntime(user, FakeButton(user, position), position)
            for position, user in enumerate(users, start=1)
        }

        browser._update_user_menu()

        account_actions = [
            action for action in browser.parent.menuUsers.actions()
            if not action.isSeparator() and action.shortcut().toString() != "Ctrl+U"
        ]
        self.assertEqual(
            [action.shortcut().toString() for action in account_actions],
            ["Ctrl+1", "Ctrl+2"],
        )
        account_actions[1].trigger()
        browser.activate_account.assert_called_once_with("third")


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
