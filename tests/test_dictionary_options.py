"""Regression tests for dictionary discovery and presentation."""

from types import SimpleNamespace
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
        self.selected_dictionaries = ["pt_BR"]
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

    def get_selected_dictionaries(self):
        return list(self.selected_dictionaries)

    def get_download_path(self):
        return "/downloads"

    def list_available_languages(self):
        return ["en"]

    def get_current_language(self):
        return "system"

    def set_dictionary_language(self, language):
        self.saved_dictionary = language


class DictionarySettingsUiTests(QtTestCase):

    def test_interface_reload_restores_lazy_settings_page_by_stable_id(self):
        current_settings = SimpleNamespace(current_page_id="debugging")
        next_settings = SimpleNamespace(open_page_id=Mock())
        window = SimpleNamespace(app_settings=current_settings)

        def close_settings():
            window.app_settings = None

        def open_settings():
            window.app_settings = next_settings

        window.close_settings = close_settings
        window.open_settings = open_settings
        app = SimpleNamespace(getWindow=lambda: window)

        reloaded = LanguageDownloadSettingsController._reload_open_settings_page(
            app
        )

        self.assertTrue(reloaded)
        next_settings.open_page_id.assert_called_once_with("debugging")

    def test_settings_page_displays_selected_language_summary(self):
        model = FakeLanguageDownloadSettingsModel()
        with patch(
            "zapzap.features.settings.pages.language_downloads.controller."
            "LanguageDownloadSettingsModel",
            return_value=model,
        ):
            page = LanguageDownloadSettingsController()

        self.assertEqual(
            page.spell_languages_row.description_label.text(),
            "Portuguese (Brazil)",
        )
        self.assertEqual(page.btn_select_spell_languages.text(), "Select…")

    def test_settings_summary_updates_after_selection_changes(self):
        model = FakeLanguageDownloadSettingsModel()
        with patch(
            "zapzap.features.settings.pages.language_downloads.controller."
            "LanguageDownloadSettingsModel",
            return_value=model,
        ):
            page = LanguageDownloadSettingsController()

        model.selected_dictionaries = ["custom_dictionary", "pt_BR"]
        model.dictionary_options = [
            DictionaryOption(
                "custom_dictionary",
                "A customized dictionary with a substantially longer name",
            ),
            DictionaryOption("pt_BR", "Portuguese (Brazil)"),
        ]
        page._update_spellcheck_language_summary()

        self.assertEqual(
            page.spell_languages_row.description_label.text(),
            "A customized dictionary with a substantially longer name and 1 more",
        )

    def test_browser_menu_is_compact_and_opens_picker(self):
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
                self.picker_opened = False

            @staticmethod
            def page():
                return FakePage()

            @staticmethod
            def _toggle_spellcheck(_enabled):
                pass

            def _open_spellcheck_language_picker(self):
                self.picker_opened = True

        web_view = FakeWebView()
        menu = QMenu()
        with patch.object(
            DictionariesManager,
            "options",
            side_effect=AssertionError("the context menu must not enumerate dictionaries"),
        ):
            WebView._add_spellcheck_actions(web_view, menu)

        spellcheck_action, languages_action = menu.actions()
        self.assertEqual(spellcheck_action.text(), "Check Spelling")
        self.assertTrue(spellcheck_action.isCheckable())
        self.assertEqual(languages_action.text(), "Languages…")
        self.assertIsNone(languages_action.menu())
        self.assertEqual(len(menu.actions()), 2)

        languages_action.trigger()
        self.assertTrue(web_view.picker_opened)

    def test_browser_languages_action_is_visible_but_disabled_when_off(self):
        profile = Mock()
        profile.isSpellCheckEnabled.return_value = False

        class FakeWebView(QWidget):
            def page(self):
                page = Mock()
                page.profile.return_value = profile
                return page

            @staticmethod
            def _toggle_spellcheck(_enabled):
                pass

            @staticmethod
            def _open_spellcheck_language_picker():
                pass

        fake = FakeWebView()
        menu = QMenu()

        WebView._add_spellcheck_actions(fake, menu)

        self.assertEqual(len(menu.actions()), 2)
        self.assertFalse(menu.actions()[1].isEnabled())


if __name__ == "__main__":
    unittest.main()
