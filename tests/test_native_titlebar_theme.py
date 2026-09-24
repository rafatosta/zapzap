"""Regression tests for synchronizing native window decoration color scheme."""

import unittest
from unittest.mock import patch

from PyQt6.QtCore import Qt

from zapzap.core.theme.theme_manager import ThemeManager


class NativeTitlebarThemeTests(unittest.TestCase):

    class StyleHints:
        def __init__(self):
            self.set_calls = []
            self.unset_calls = 0

        def setColorScheme(self, scheme):
            self.set_calls.append(scheme)

        def unsetColorScheme(self):
            self.unset_calls += 1

    class LegacyStyleHints:
        pass

    class App:
        def __init__(self, style_hints):
            self._style_hints = style_hints

        def styleHints(self):
            return self._style_hints

    def test_dark_theme_sets_native_dark_color_scheme(self):
        hints = self.StyleHints()
        app = self.App(hints)

        with patch.object(ThemeManager, "_get_app_instance", return_value=app):
            applied = ThemeManager._apply_native_color_scheme_hint(
                ThemeManager.Type.Dark,
                Qt.ColorScheme.Dark,
            )

        self.assertTrue(applied)
        self.assertEqual(hints.set_calls, [Qt.ColorScheme.Dark])
        self.assertEqual(hints.unset_calls, 0)

    def test_light_theme_sets_native_light_color_scheme(self):
        hints = self.StyleHints()
        app = self.App(hints)

        with patch.object(ThemeManager, "_get_app_instance", return_value=app):
            applied = ThemeManager._apply_native_color_scheme_hint(
                ThemeManager.Type.Light,
                Qt.ColorScheme.Light,
            )

        self.assertTrue(applied)
        self.assertEqual(hints.set_calls, [Qt.ColorScheme.Light])

    def test_auto_theme_releases_override_back_to_system(self):
        hints = self.StyleHints()
        app = self.App(hints)

        with patch.object(ThemeManager, "_get_app_instance", return_value=app):
            applied = ThemeManager._apply_native_color_scheme_hint(
                ThemeManager.Type.Auto,
                Qt.ColorScheme.Dark,
            )

        self.assertTrue(applied)
        self.assertEqual(hints.set_calls, [])
        self.assertEqual(hints.unset_calls, 1)

    def test_legacy_qt_without_setter_is_compatible(self):
        app = self.App(self.LegacyStyleHints())

        with patch.object(ThemeManager, "_get_app_instance", return_value=app):
            applied = ThemeManager._apply_native_color_scheme_hint(
                ThemeManager.Type.Dark,
                Qt.ColorScheme.Dark,
            )

        self.assertFalse(applied)


if __name__ == "__main__":
    unittest.main(verbosity=2)
