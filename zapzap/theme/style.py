from PyQt6.QtCore import QSettings
from .style_components.qwidgets import QWIDGETS
from .style_components.menu_home import MENU_HOME
from .style_components.settings import SETTINGS
from .style_components.popup import POPUP
import zapzap


def buildTheme(p) -> str:

    settings = QSettings(zapzap.__appname__, zapzap.__appname__)

    STYLE_SHEET = f"""
        {QWIDGETS}
        {MENU_HOME}
        {SETTINGS}
        {POPUP}
        """

    for chave, valor in p.getPallete().items():
        STYLE_SHEET = STYLE_SHEET.replace("{"+chave+"}", valor)

    return STYLE_SHEET
