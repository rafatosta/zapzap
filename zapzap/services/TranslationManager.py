import gettext
import os
from PyQt6.QtCore import QLocale

from zapzap import APP_PATH, __appname__
from zapzap.services.SettingsManager import SettingsManager


class TranslationManager:

    _domain = "zapzap"
    _locale_dir = os.path.join(APP_PATH, "po")
    SYSTEM_LANGUAGE = "system"
    ENGLISH_LANGUAGE = "en"

    @staticmethod
    def list_available_languages():
        languages = [TranslationManager.ENGLISH_LANGUAGE]
        if not os.path.isdir(TranslationManager._locale_dir):
            return languages

        for locale in sorted(
            os.listdir(TranslationManager._locale_dir), key=str.casefold
        ):
            mo_path = os.path.join(
                TranslationManager._locale_dir,
                locale,
                "LC_MESSAGES",
                f"{TranslationManager._domain}.mo",
            )
            if os.path.isfile(mo_path) and locale not in languages:
                languages.append(locale)

        return languages

    @staticmethod
    def get_current_language():
        language = SettingsManager.get(
            "system/interface_language", TranslationManager.SYSTEM_LANGUAGE
        )
        return language or TranslationManager.SYSTEM_LANGUAGE

    @staticmethod
    def set_current_language(language):
        if not language or language == TranslationManager.SYSTEM_LANGUAGE:
            SettingsManager.set(
                "system/interface_language", TranslationManager.SYSTEM_LANGUAGE
            )
            return

        SettingsManager.set("system/interface_language", language)

    @staticmethod
    def apply():
        # Define path to translation files
        selected_language = TranslationManager.get_current_language()
        locale_candidates = []

        if selected_language != TranslationManager.SYSTEM_LANGUAGE:
            locale_candidates.append(selected_language)
            # Most UI modules import `gettext.gettext` directly as `_` before
            # TranslationManager.apply() runs.  Setting LANGUAGE makes those
            # already-imported gettext aliases resolve the persisted language
            # too, instead of only updating the builtins installed below.
            os.environ["LANGUAGE"] = selected_language
        else:
            # Honor explicit env overrides first.
            for env_name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
                raw_value = os.environ.get(env_name, "")
                if not raw_value:
                    continue
                for item in raw_value.split(":"):
                    locale = item.split(".", 1)[0].split("@", 1)[0].strip()
                    if locale:
                        locale_candidates.append(locale)

            # Flatpak may expose locale reliably through Qt even when env vars are odd.
            qt_locale = QLocale.system().name()
            if qt_locale:
                locale_candidates.append(qt_locale)

        gettext.bindtextdomain(
            __appname__.lower(), TranslationManager._locale_dir
        )
        gettext.textdomain(__appname__.lower())

        # Keep order, remove duplicates.
        seen = set()
        normalized_candidates = []
        for locale in locale_candidates:
            if locale in seen:
                continue
            seen.add(locale)
            normalized_candidates.append(locale)

        translation = gettext.translation(
            __appname__.lower(),
            localedir=TranslationManager._locale_dir,
            languages=normalized_candidates or None,
            fallback=True,
        )
        translation.install()
