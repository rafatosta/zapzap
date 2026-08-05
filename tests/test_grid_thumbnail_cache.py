from types import SimpleNamespace
from unittest.mock import Mock

from PyQt6.QtGui import QPixmap

from qt_test_case import QtTestCase
from zapzap.features.browser.shell.browser_controller import (
    AccountLifecycle,
    AccountRuntime,
    BrowserController,
)
from zapzap.features.browser.shell.grid_thumbnail_cache import (
    GRID_THUMBNAIL_MAX_PHYSICAL_SIZE,
    GridThumbnailCache,
)


class GridThumbnailCacheTest(QtTestCase):
    def test_large_capture_is_reduced_before_it_is_retained(self):
        cache = GridThumbnailCache()

        thumbnail = cache.store("account", QPixmap(1920, 1080))

        self.assertEqual(thumbnail.size().width(), 480)
        self.assertEqual(thumbnail.size().height(), 270)
        self.assertIs(cache.get("account"), thumbnail)

    def test_hidpi_capture_stays_within_physical_pixel_limit(self):
        capture = QPixmap(1600, 1000)
        capture.setDevicePixelRatio(2.0)

        thumbnail = GridThumbnailCache().store("account", capture)

        self.assertLessEqual(
            thumbnail.width(), GRID_THUMBNAIL_MAX_PHYSICAL_SIZE.width()
        )
        self.assertLessEqual(
            thumbnail.height(), GRID_THUMBNAIL_MAX_PHYSICAL_SIZE.height()
        )
        self.assertEqual(thumbnail.devicePixelRatio(), 1.0)

    def test_replacement_keeps_one_entry_and_releases_the_previous_value(self):
        cache = GridThumbnailCache()
        first = cache.store("account", QPixmap(800, 600))

        second = cache.store("account", QPixmap(1200, 600))

        self.assertEqual(len(cache), 1)
        self.assertIs(cache.get("account"), second)
        self.assertIsNot(first, second)

    def test_null_capture_is_a_neutral_cache_miss(self):
        cache = GridThumbnailCache()

        self.assertIsNone(cache.store("account", QPixmap()))
        self.assertIsNone(cache.get("account"))
        self.assertEqual(len(cache), 0)


class BrowserGridThumbnailLifecycleTest(QtTestCase):
    class ControllerHarness:
        _capture_grid_thumbnail = BrowserController._capture_grid_thumbnail
        _grid_thumbnail = BrowserController._grid_thumbnail
        _switch_from_grid = BrowserController._switch_from_grid
        _active_runtimes = BrowserController._active_runtimes
        _create_webview = BrowserController._create_webview
        _destroy_webview = BrowserController._destroy_webview
        _ensure_valid_selection = BrowserController._ensure_valid_selection
        disable_page = BrowserController.disable_page
        delete_page = BrowserController.delete_page
        close_pages = BrowserController.close_pages
        reload_pages = BrowserController.reload_pages

    class FakeWebView:
        def __init__(self, user_id="account", enabled=True):
            self.user = SimpleNamespace(id=user_id, enable=enabled)
            self.shutdown = Mock()
            self.disable_page = Mock()
            self.enable_page = Mock()
            self.remove_files = Mock()
            self.close = Mock()
            self.setParent = Mock()
            self.deleteLater = Mock()
            self.load_page = Mock()

    @staticmethod
    def _controller():
        controller = BrowserGridThumbnailLifecycleTest.ControllerHarness()
        controller._shutting_down = False
        controller._grid_thumbnails = GridThumbnailCache()
        controller._accounts = {}
        controller._last_active_webview = None
        controller._update_total_notifications = Mock()
        return controller

    @staticmethod
    def _page(user_id="account", visible=True, enabled=True):
        page = Mock()
        page.user = SimpleNamespace(id=user_id, enable=enabled)
        page._shutting_down = False
        page.isVisible.return_value = visible
        page.grab.return_value = QPixmap(960, 540)
        return page

    def test_repeated_grid_lookup_reuses_one_thumbnail(self):
        controller = self._controller()
        page = self._page()

        first = controller._grid_thumbnail(page)
        second = controller._grid_thumbnail(page)

        self.assertIs(first, second)
        self.assertEqual(page.grab.call_count, 1)
        self.assertEqual(len(controller._grid_thumbnails), 1)

    def test_hidden_page_without_cache_uses_fallback_without_grab(self):
        controller = self._controller()
        page = self._page(visible=False)

        self.assertIsNone(controller._grid_thumbnail(page))
        page.grab.assert_not_called()

    def test_disabled_and_shutting_down_pages_are_not_captured(self):
        controller = self._controller()
        disabled = self._page(enabled=False)
        shutting_down = self._page(user_id="closing")
        shutting_down._shutting_down = True

        self.assertIsNone(controller._capture_grid_thumbnail(disabled))
        self.assertIsNone(controller._capture_grid_thumbnail(shutting_down))
        disabled.grab.assert_not_called()
        shutting_down.grab.assert_not_called()

    def test_invalidation_and_clear_release_entries(self):
        cache = GridThumbnailCache()
        cache.store("disabled", QPixmap(10, 10))
        cache.store("deleted", QPixmap(10, 10))
        cache.invalidate("disabled")

        self.assertIsNone(cache.get("disabled"))
        self.assertIsNotNone(cache.get("deleted"))

        cache.clear()
        self.assertEqual(len(cache), 0)

    def test_disable_path_invalidates_before_tearing_down_page(self):
        controller = self._controller()
        page = self.FakeWebView(enabled=False)
        button = Mock()
        runtime = AccountRuntime(page.user, button, 1, page,
                                 AccountLifecycle.ACTIVE)
        controller._accounts = {page.user.id: runtime}
        controller.pages = Mock()
        controller.pages.currentWidget.return_value = page
        controller._grid_thumbnails.store("account", QPixmap(10, 10))
        controller._select_default_page = Mock()
        controller._update_user_menu = Mock()

        controller.disable_page(page.user)

        self.assertIsNone(controller._grid_thumbnails.get("account"))
        page.disable_page.assert_called_once_with()

    def test_delete_path_invalidates_and_preserves_webview_shutdown(self):
        controller = self._controller()
        page = self.FakeWebView(user_id="deleted")
        button = SimpleNamespace(
            page_index=3,
            close=Mock(),
            deleteLater=Mock(),
        )
        runtime = AccountRuntime(page.user, button, 3, page,
                                 AccountLifecycle.ACTIVE)
        controller._accounts = {page.user.id: runtime}
        controller.pages = Mock()
        controller._grid_thumbnails.store("deleted", QPixmap(10, 10))
        controller._select_default_page = Mock()
        controller._update_user_menu = Mock()

        controller.delete_page(page.user)

        self.assertIsNone(controller._grid_thumbnails.get("deleted"))
        page.shutdown.assert_called_once_with()
        page.remove_files.assert_called_once_with()

    def test_close_pages_clears_cache_and_grid_before_webviews(self):
        controller = self._controller()
        page = self.FakeWebView(user_id="closing")
        controller._grid_thumbnails.store("closing", QPixmap(10, 10))
        controller.grid_view = Mock()
        button = SimpleNamespace(close=Mock(), deleteLater=Mock())
        controller._accounts = {
            "closing": AccountRuntime(
                page.user, button, 1, page, AccountLifecycle.ACTIVE
            )
        }
        controller.pages = Mock()
        controller.close_pages()

        self.assertEqual(len(controller._grid_thumbnails), 0)
        controller.grid_view.clear_thumbnails.assert_called_once_with()
        page.shutdown.assert_called_once_with()

    def test_reload_invalidates_all_account_thumbnails(self):
        controller = self._controller()
        first = self.FakeWebView(user_id="first")
        second = self.FakeWebView(user_id="second")
        controller._grid_thumbnails.store("first", QPixmap(10, 10))
        controller._grid_thumbnails.store("second", QPixmap(10, 10))
        controller.grid_view = Mock()
        controller._accounts = {
            "first": AccountRuntime(
                first.user, Mock(), 1, first, AccountLifecycle.ACTIVE
            ),
            "second": AccountRuntime(
                second.user, Mock(), 2, second, AccountLifecycle.ACTIVE
            ),
        }

        controller.reload_pages()

        self.assertEqual(len(controller._grid_thumbnails), 0)
        controller.grid_view.clear_thumbnails.assert_called_once_with()
        first.load_page.assert_called_once_with()
        second.load_page.assert_called_once_with()

    def test_grid_thumbnail_click_keeps_account_selection_by_stable_id(self):
        controller = self._controller()
        controller.activate_account = Mock()

        controller._switch_from_grid("target")

        controller.activate_account.assert_called_once_with("target")
