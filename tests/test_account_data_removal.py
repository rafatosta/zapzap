"""Regression tests for deleting an account's data from disk."""

import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace

from PyQt6.QtCore import QCoreApplication, QEvent

from qt_test_case import QtTestCase
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.web.web_view import WebView


class _Account:
    """Stands in for a WebView, exposing only what remove_files touches.

    Instantiating a real WebView pulls in QtWebEngine, which needs a
    QApplication built with a program name. remove_files is called unbound so
    the real implementation still runs.
    """

    def __init__(self, cache_path, storage_path, resolved):
        self._cache_path = cache_path
        self._storage_path = storage_path
        self.user = SimpleNamespace(id="account-1")
        self._resolved = resolved
        self.resolve_calls = 0

    def profile_paths(self, user_id):
        self.resolve_calls += 1
        return self._resolved


class AccountDataRemovalTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="zapzap-account-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.cache = self._make("cache")
        self.storage = self._make("storage")

    def _make(self, name):
        path = os.path.join(self.root, name)
        os.makedirs(path)
        with open(os.path.join(path, "session.dat"), "w") as handle:
            handle.write("session")
        return path

    def _remove(self, account):
        WebView.remove_files(account)

    def test_data_of_an_account_disabled_since_startup_is_removed(self):
        # The profile was never opened, so no paths were captured.
        account = _Account(None, None, (self.cache, self.storage))

        self._remove(account)

        self.assertFalse(os.path.exists(self.cache))
        self.assertFalse(os.path.exists(self.storage))
        self.assertEqual(account.resolve_calls, 1)

    def test_captured_paths_are_used_without_reopening_the_profile(self):
        account = _Account(self.cache, self.storage, ("/nonexistent", "/nope"))

        self._remove(account)

        self.assertFalse(os.path.exists(self.cache))
        self.assertFalse(os.path.exists(self.storage))
        self.assertEqual(account.resolve_calls, 0)

    def test_paths_are_cleared_so_removal_is_not_repeated(self):
        account = _Account(self.cache, self.storage, (self.cache, self.storage))

        self._remove(account)

        self.assertIsNone(account._cache_path)
        self.assertIsNone(account._storage_path)

    def test_missing_directories_are_tolerated(self):
        shutil.rmtree(self.cache)
        shutil.rmtree(self.storage)
        account = _Account(self.cache, self.storage, (self.cache, self.storage))

        self._remove(account)  # must not raise

        self.assertFalse(os.path.exists(self.cache))


class DisabledAccountWebViewTest(QtTestCase):
    """The same removal, driven through a real WebView."""

    def test_data_is_removed_for_an_account_disabled_since_startup(self):
        user = User(id="account-disabled", name="Disabled", enable=False)
        view = WebView(user=user, page_index=0)
        self.addCleanup(view.deleteLater)

        # The profile was never opened, so the WebView holds no paths.
        self.assertIsNone(view._cache_path)
        self.assertIsNone(view._storage_path)

        cache, storage = WebView.profile_paths(user.id)
        # profile_paths schedules its probe with deleteLater, which only runs
        # on an event loop turn. Release it before remove_files opens a second
        # profile under the same name.
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

        for path in (cache, storage):
            os.makedirs(path, exist_ok=True)
        session = os.path.join(storage, "session.dat")
        with open(session, "w") as handle:
            handle.write("session")

        view.remove_files()

        self.assertFalse(os.path.exists(cache))
        self.assertFalse(os.path.exists(storage))
        self.assertFalse(os.path.exists(session))


if __name__ == "__main__":
    unittest.main()
