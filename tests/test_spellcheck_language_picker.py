"""Regression tests for multi-language spellcheck selection."""

import tempfile
from unittest.mock import Mock, patch

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QDialog, QGraphicsDropShadowEffect, QPushButton

from qt_test_case import QtTestCase
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.browser.web.web_view import WebView
from zapzap.features.dictionaries.dictionaries_manager import (
    DictionariesManager,
    DictionaryOption,
)
from zapzap.features.dictionaries.spellcheck_language_picker import (
    open_spellcheck_language_picker,
)
from zapzap.ui.components import SpellcheckLanguagePickerDialog


class DictionarySelectionManagerTests(QtTestCase):

    def setUp(self):
        super().setUp()
        self._temporary = tempfile.TemporaryDirectory(prefix="spellcheck-settings-")
        self._original_settings = SettingsManager._settings
        SettingsManager._settings = QSettings(
            f"{self._temporary.name}/settings.ini",
            QSettings.Format.IniFormat,
        )
        self.options = [
            DictionaryOption("en_US", "English (United States)"),
            DictionaryOption("pt_BR", "Portuguese (Brazil)"),
            DictionaryOption("es_ES", "Spanish (Spain)"),
        ]
        self.options_patch = patch.object(
            DictionariesManager,
            "options",
            return_value=self.options,
        )
        self.options_patch.start()

    def tearDown(self):
        self.options_patch.stop()
        SettingsManager._settings = self._original_settings
        self._temporary.cleanup()
        super().tearDown()

    def test_legacy_scalar_is_migrated_without_removing_legacy_key(self):
        SettingsManager.set("system/spellCheckLanguage", "pt_BR")

        self.assertEqual(
            DictionariesManager.get_selected_languages(),
            ["pt_BR"],
        )
        self.assertEqual(
            SettingsManager.get("system/spellCheckLanguages"),
            ["pt_BR"],
        )
        self.assertEqual(
            SettingsManager.get("system/spellCheckLanguage"),
            "pt_BR",
        )

    def test_selection_deduplicates_valid_codes_preserves_order_and_limit(self):
        many_options = [
            DictionaryOption(f"custom_{index:02d}", f"Language {index:02d}")
            for index in range(12)
        ]
        self.options_patch.stop()
        self.options_patch = patch.object(
            DictionariesManager,
            "options",
            return_value=many_options,
        )
        self.options_patch.start()

        DictionariesManager.set_selected_languages(
            ["custom_02", "missing", "custom_02"]
            + [f"custom_{index:02d}" for index in range(12)]
        )

        self.assertEqual(
            DictionariesManager.get_selected_languages(),
            ["custom_02", "custom_00", "custom_01"]
            + [f"custom_{index:02d}" for index in range(3, 10)],
        )

    def test_invalid_selection_falls_back_and_current_dict_is_compatible(self):
        SettingsManager.set("system/spellCheckLanguages", ["removed"])
        SettingsManager.set("system/spellCheckLanguage", "also_removed")
        with patch.object(
            DictionariesManager,
            "get_system_language",
            return_value="pt_BR",
        ):
            selected = DictionariesManager.get_selected_languages()

        self.assertEqual(selected, ["pt_BR"])
        self.assertEqual(DictionariesManager.get_current_dict(), "pt_BR")

    def test_recents_are_deduplicated_validated_and_capped(self):
        DictionariesManager.update_recent_languages(
            ["pt_BR", "en_US", "pt_BR", "missing", "es_ES"]
        )
        DictionariesManager.update_recent_languages(["es_ES", "pt_BR"])

        self.assertEqual(
            DictionariesManager.get_recent_languages(),
            ["es_ES", "pt_BR", "en_US"],
        )


class SpellcheckLanguagePickerUiTests(QtTestCase):

    def make_dialog(self, options=None, selected=None, recent=None):
        return SpellcheckLanguagePickerDialog(
            options if options is not None else [
                DictionaryOption("en_US", "English (United States)"),
                DictionaryOption("pt_BR", "Português (Brasil)"),
                DictionaryOption("es_ES", "Español (España)"),
            ],
            selected if selected is not None else ["pt_BR"],
            recent if recent is not None else ["en_US", "pt_BR"],
            maximum_selected=DictionariesManager.MAX_SELECTED_LANGUAGES,
            maximum_recent=DictionariesManager.MAX_RECENT_LANGUAGES,
        )

    def test_search_matches_label_code_and_ignores_accents(self):
        dialog = self.make_dialog()

        for query in ("portugues", "Português", "pt_BR", "brasil"):
            dialog.search_edit.setText(query)
            self.assertFalse(dialog._language_items["pt_BR"].isHidden(), query)
            self.assertTrue(dialog._language_items["en_US"].isHidden(), query)

    def test_escape_clears_search_before_rejecting(self):
        dialog = self.make_dialog()
        dialog.search_edit.setText("portugues")
        escape = Mock()
        escape.key.return_value = Qt.Key.Key_Escape

        dialog.keyPressEvent(escape)

        self.assertEqual(dialog.search_edit.text(), "")
        escape.accept.assert_called_once_with()

    def test_selection_is_staged_and_last_language_is_protected(self):
        dialog = self.make_dialog()
        portuguese = dialog._language_items["pt_BR"]
        portuguese.setCheckState(Qt.CheckState.Unchecked)

        self.assertEqual(dialog.selected_languages, ["pt_BR"])
        self.assertEqual(portuguese.checkState(), Qt.CheckState.Checked)
        self.assertEqual(
            dialog.feedback_label.text(),
            "At least one language must remain selected.",
        )

        dialog._language_items["en_US"].setCheckState(Qt.CheckState.Checked)
        self.assertEqual(dialog.selected_languages, ["pt_BR", "en_US"])
        self.assertTrue(dialog.apply_button.isEnabled())

    def test_limit_disables_only_unselected_languages(self):
        options = [
            DictionaryOption(f"lang_{index:02d}", f"Language {index:02d}")
            for index in range(11)
        ]
        dialog = self.make_dialog(
            options=options,
            selected=[option.code for option in options[:10]],
            recent=[],
        )

        self.assertTrue(dialog._language_items["lang_00"].flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertFalse(dialog._language_items["lang_10"].flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertEqual(dialog.selected_count_label.text(), "10/10")

    def test_recents_exclude_selected_and_add_to_staged_selection(self):
        dialog = self.make_dialog()
        self.assertTrue(dialog.recent_section.isVisibleTo(dialog))
        recent_button = dialog.recent_layout.itemAt(0).widget()

        recent_button.click()

        self.assertEqual(dialog.selected_languages, ["pt_BR", "en_US"])
        self.assertFalse(dialog.recent_section.isVisibleTo(dialog))

    def test_empty_search_and_no_dictionary_states_are_stable(self):
        dialog = self.make_dialog()
        dialog.search_edit.setText("does-not-exist")
        self.assertFalse(dialog.empty_search_label.isHidden())
        self.assertTrue(dialog.language_list.isHidden())

        empty = self.make_dialog(options=[], selected=[], recent=[])
        self.assertFalse(empty.no_dictionaries.isHidden())
        self.assertTrue(empty.manage_button.isEnabled())
        self.assertFalse(empty.apply_button.isEnabled())

    def test_large_list_keeps_one_item_per_language_and_bounded_size(self):
        options = [
            DictionaryOption(f"lang_{index:03d}", f"Language {index:03d}")
            for index in range(150)
        ]
        dialog = self.make_dialog(options=options, selected=["lang_000"], recent=[])

        self.assertEqual(len(dialog._language_items), 150)
        self.assertLessEqual(dialog.width(), dialog.maximumWidth())
        self.assertEqual(
            dialog.language_list.horizontalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        self.assertTrue(dialog.search_edit.accessibleName())
        self.assertTrue(dialog.language_list.accessibleDescription())

    def test_dialog_uses_the_shared_rounded_frameless_window_treatment(self):
        dialog = self.make_dialog()

        self.assertTrue(
            dialog.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        )
        self.assertEqual(
            dialog.window_frame.objectName(),
            "SpellcheckPickerWindowFrame",
        )
        self.assertIsInstance(
            dialog.window_frame.graphicsEffect(),
            QGraphicsDropShadowEffect,
        )
        self.assertIn(
            f"border-radius: {dialog.WINDOW_RADIUS}px",
            dialog.styleSheet(),
        )


class SpellcheckLanguagePickerIntegrationTests(QtTestCase):

    def test_accept_persists_selection_updates_recents_and_profiles(self):
        fake_dialog = Mock()
        fake_dialog.manage_button = QPushButton()
        fake_dialog.exec.return_value = QDialog.DialogCode.Accepted
        fake_dialog.selected_languages = ["pt_BR", "en_US"]
        on_applied = Mock()

        with (
            patch(
                "zapzap.features.dictionaries.spellcheck_language_picker."
                "SpellcheckLanguagePickerDialog",
                return_value=fake_dialog,
            ),
            patch.object(DictionariesManager, "options", return_value=[]),
            patch.object(DictionariesManager, "get_selected_languages", return_value=[]),
            patch.object(DictionariesManager, "get_recent_languages", return_value=[]),
            patch.object(DictionariesManager, "set_selected_languages") as save,
            patch.object(DictionariesManager, "update_recent_languages") as recent,
        ):
            accepted = open_spellcheck_language_picker(on_applied=on_applied)

        self.assertTrue(accepted)
        save.assert_called_once_with(["pt_BR", "en_US"])
        recent.assert_called_once_with(["pt_BR", "en_US"])
        on_applied.assert_called_once_with()

    def test_cancel_does_not_persist(self):
        fake_dialog = Mock()
        fake_dialog.manage_button = QPushButton()
        fake_dialog.exec.return_value = QDialog.DialogCode.Rejected
        with (
            patch(
                "zapzap.features.dictionaries.spellcheck_language_picker."
                "SpellcheckLanguagePickerDialog",
                return_value=fake_dialog,
            ),
            patch.object(DictionariesManager, "options", return_value=[]),
            patch.object(DictionariesManager, "get_selected_languages", return_value=[]),
            patch.object(DictionariesManager, "get_recent_languages", return_value=[]),
            patch.object(DictionariesManager, "set_selected_languages") as save,
        ):
            accepted = open_spellcheck_language_picker()

        self.assertFalse(accepted)
        save.assert_not_called()

    def test_packaged_flatpak_catalog_hides_the_management_action(self):
        fake_dialog = Mock()
        fake_dialog.manage_button = QPushButton()
        fake_dialog.exec.return_value = QDialog.DialogCode.Rejected
        with (
            patch(
                "zapzap.features.dictionaries.spellcheck_language_picker."
                "SpellcheckLanguagePickerDialog",
                return_value=fake_dialog,
            ),
            patch.object(DictionariesManager, "options", return_value=[]),
            patch.object(DictionariesManager, "get_selected_languages", return_value=[]),
            patch.object(DictionariesManager, "get_recent_languages", return_value=[]),
            patch.object(
                DictionariesManager,
                "is_management_available",
                return_value=False,
            ),
        ):
            open_spellcheck_language_picker()

        self.assertTrue(fake_dialog.manage_button.isHidden())

    def test_webview_configures_the_complete_language_list(self):
        profile = Mock()
        fake = Mock()
        fake.user.enable = True
        fake.profile = profile

        with patch.object(
            DictionariesManager,
            "get_selected_languages",
            return_value=["pt_BR", "en_US"],
        ):
            WebView.configure_spellcheck(fake)

        profile.setSpellCheckLanguages.assert_called_once_with(["pt_BR", "en_US"])

    def test_webview_disables_spellcheck_when_qt_rejects_languages(self):
        profile = Mock()
        profile.setSpellCheckLanguages.side_effect = [
            RuntimeError("simulated dictionary failure"),
            None,
        ]
        fake = Mock()
        fake.user.enable = True
        fake.profile = profile

        with (
            patch.object(
                DictionariesManager,
                "get_selected_languages",
                return_value=["invalid"],
            ),
            self.assertLogs(
                "zapzap.features.browser.web.web_view",
                level="ERROR",
            ),
        ):
            WebView.configure_spellcheck(fake)

        self.assertEqual(
            profile.setSpellCheckLanguages.call_args_list[-1].args[0],
            [],
        )
        profile.setSpellCheckEnabled.assert_called_with(False)


if __name__ == "__main__":
    import unittest

    unittest.main()
