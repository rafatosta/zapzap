import gettext
import os

from zapzap import APP_PATH, __appname__


class TranslationManager:

    _domain = "zapzap"
    _locale_dir = os.path.join(APP_PATH, "po")

    @staticmethod
    def apply():
        print("Locale dir:", TranslationManager._locale_dir)
         # Define path to translation files
        gettext.bindtextdomain(__appname__.lower(),
                            TranslationManager._locale_dir)
        gettext.textdomain(__appname__.lower())
