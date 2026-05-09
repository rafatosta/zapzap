import gettext
import os
from PyQt6.QtCore import QLocale

from zapzap import APP_PATH, __appname__


class TranslationManager:

    _domain = "zapzap"
    _locale_dir = os.path.join(APP_PATH, "po")

    @staticmethod
    def apply():
        # Define path to translation files
        gettext.bindtextdomain(__appname__.lower(),
                            TranslationManager._locale_dir)
        gettext.textdomain(__appname__.lower())

        locale_candidates = []

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
