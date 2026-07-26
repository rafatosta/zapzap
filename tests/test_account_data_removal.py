"""Regression tests for deleting an account's data from disk."""

import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace

import qt_test_case  # noqa: F401  puts the repository root on sys.path
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


if __name__ == "__main__":
    unittest.main()
