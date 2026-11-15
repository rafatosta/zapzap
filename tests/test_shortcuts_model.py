"""Regression tests for the keyboard shortcuts dialog data."""

import unittest

from zapzap.features.shortcuts.model import ShortcutsModel


class ShortcutsModelTests(unittest.TestCase):
    def test_theme_shortcuts_avoid_altgr_combinations(self):
        shortcuts = dict(
            (name, keys) for name, keys in ShortcutsModel().zapzap_shortcuts()
        )

        self.assertEqual(shortcuts["Automatic theme"], "Ctrl + Shift + 1")
        self.assertEqual(shortcuts["Light theme"], "Ctrl + Shift + 2")
        self.assertEqual(shortcuts["Dark theme"], "Ctrl + Shift + 3")
        for name in ("Automatic theme", "Light theme", "Dark theme"):
            self.assertNotIn("Alt", shortcuts[name])


if __name__ == "__main__":
    unittest.main()
