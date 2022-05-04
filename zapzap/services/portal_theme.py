from PyQt6.QtWidgets import QApplication
from zapzap import theme_light_path, theme_dark_path


def isDarktheme():
    current_style = QApplication.instance().style().objectName()
    if 'Dark'.upper() in current_style.upper():
        return True
    else:
        return False


def loadStylesheet(app):
    # Pega o tema atual do sistema
    current_style = app.style().objectName()

    # Verifica se existe a palavra dark no tema
    if 'Dark'.upper() in current_style.upper():
        path = theme_dark_path
    else:
        path = theme_light_path

    with open(path, 'r') as f:
        style = f.read()
    app.setStyleSheet(style)

    #theme_mode = window.settings.value("system/night_mode", False, bool)
    """if isNight_mode:
        path = theme_dark_path
    else:
        path = theme_light_path

    self.browser.whats.setTheme(isNight_mode)
    with open(path, 'r') as f:
        style = f.read()

    # Set the stylesheet of the application
    self.app.setStyleSheet(style)"""
