"""Regression tests for dictionary discovery and presentation."""

import unittest
from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QMenu, QWidget

from qt_test_case import QtTestCase
from zapzap.features.browser.web.web_view import WebView
from zapzap.features.dictionaries.dictionaries_manager import (
    DictionariesManager,
    DictionaryOption,
)
from zapzap.features.settings.pages.language_downloads.controller import (
    LanguageDownloadSettingsController,
)


class DictionaryOptionsTests(unittest.TestCase):

    def test_type_annotations_do_not_resolve_list_as_the_manager_method(self):
        self.assertEqual(
            DictionariesManager.options.__annotations__["return"],
            "list[DictionaryOption]",
        )

    def test_options_are_readable_and_sorted_without_filtering_custom_names(self):
        with (
            patch.object(DictionariesManager, "get_path", return_value="/dictionaries"),
            patch(
                "zapzap.features.dictionaries.dictionaries_manager.os.path.isdir",
                return_value=True,
            ),
            patch(
                "zapzap.features.dictionaries.dictionaries_manager.os.listdir",
                return_value=[
                    "es-ES-3-0.bdic",
                    "notes.txt",
                    "custom_brand.bdic",
                    "ar_EG.bdic",
                ],
            ),
        ):
            options = DictionariesManager.options()

        self.assertEqual(
            [(option.code, option.label) for option in options],
            [
                ("ar_EG", "Arabic (Egypt)"),
                ("custom_brand", "custom_brand"),
                ("es-ES-3-0", "Spanish (Spain)"),
            ],
        )

    def test_label_includes_an_explicit_script_without_changing_the_code(self):
        option = DictionariesManager.label("sr_Latn_RS")

        self.assertEqual(option, "Serbian (Latin, Serbia)")

    def test_language_without_explicit_territory_does_not_invent_one(self):
        self.assertEqual(DictionariesManager.label("en"), "English")


class FakeLanguageDownloadSettingsModel:

    def __init__(self):
        self.spellcheck_enabled = True
        self.saved_dictionary = None
        self.current_dictionary = "pt_BR"
        self.dictionary_options = [
            DictionaryOption("ar_EG", "Arabic (Egypt)"),
            DictionaryOption("pt_BR", "Portuguese (Brazil)"),
        ]

    def get_dictionaries_path(self):
        return "/dictionaries"

    def list_dictionary_options(self):
        return self.dictionary_options

    def get_current_dictionary(self):
        return self.current_dictionary

    def get_download_path(self):
        return "/downloads"

    def list_available_languages(self):
        return ["en"]

    def get_current_language(self):
        return "system"

    def set_dictionary_language(self, language):
        self.saved_dictionary = language


class DictionarySettingsUiTests(QtTestCase):

    def test_settings_combo_displays_labels_and_persists_item_data(self):
        model = FakeLanguageDownloadSettingsModel()
        with patch(
            "zapzap.features.settings.pages.language_downloads.controller."
            "LanguageDownloadSettingsModel",
            return_value=model,
        ):
            page = LanguageDownloadSettingsController()

        self.assertEqual(page.spell_comboBox.currentText(), "Portuguese (Brazil)")
        self.assertEqual(page.spell_comboBox.currentData(), "pt_BR")

        page._update_browser_spellcheck = Mock()
        arabic_index = page.spell_comboBox.findData("ar_EG")
        page.spell_comboBox.setCurrentIndex(arabic_index)
        page._handle_spellcheck(arabic_index)

        self.assertEqual(model.saved_dictionary, "ar_EG")
        page._update_browser_spellcheck.assert_called_once_with()

    def test_settings_combo_recalculates_width_after_dictionary_folder_change(self):
        model = FakeLanguageDownloadSettingsModel()
        with patch(
            "zapzap.features.settings.pages.language_downloads.controller."
            "LanguageDownloadSettingsModel",
            return_value=model,
        ):
            page = LanguageDownloadSettingsController()

        page.show()
        self.app.processEvents()
        initial_width = page.spell_comboBox.sizeHint().width()

        model.current_dictionary = "custom_dictionary"
        model.dictionary_options = [
            DictionaryOption(
                "custom_dictionary",
                "A customized dictionary with a substantially longer name",
            )
        ]
        page._load_settings()
        self.app.processEvents()

        self.assertGreater(page.spell_comboBox.sizeHint().width(), initial_width)
        self.assertEqual(page.spell_comboBox.currentData(), "custom_dictionary")

    def test_browser_menu_displays_labels_but_selects_dictionary_code(self):
        class FakeProfile:
            @staticmethod
            def spellCheckLanguages():
                return ["pt_BR"]

            @staticmethod
            def isSpellCheckEnabled():
                return True

        class FakePage:
            @staticmethod
            def profile():
                return FakeProfile()

        class FakeWebView(QWidget):
            def __init__(self):
                super().__init__()
                self.selected_dictionary = None

            @staticmethod
            def page():
                return FakePage()

            @staticmethod
            def _toggle_spellcheck(_enabled):
                pass

            def _select_language(self, language):
                self.selected_dictionary = language

        web_view = FakeWebView()
        menu = QMenu()
        options = [
            DictionaryOption("ar_EG", "Arabic (Egypt)"),
            DictionaryOption("pt_BR", "Portuguese (Brazil)"),
        ]
        with patch.object(DictionariesManager, "options", return_value=options):
            WebView._add_spellcheck_actions(web_view, menu)

        language_menu = menu.actions()[1].menu()
        arabic_action, portuguese_action = language_menu.actions()
        self.assertEqual(arabic_action.text(), "Arabic (Egypt)")
        self.assertEqual(arabic_action.data(), "ar_EG")
        self.assertFalse(arabic_action.isChecked())
        self.assertTrue(portuguese_action.isChecked())

        arabic_action.trigger()

        self.assertEqual(web_view.selected_dictionary, "ar_EG")


if __name__ == "__main__":
    unittest.main()
