from PyQt6.QtWidgets import QApplication
from zapzap import theme_light_path, theme_dark_path




def isDarktheme():
    app = QApplication.instance()
    current_style = app.style().objectName()
    print('Dark'.upper(), current_style.upper(), 'Dark'.upper() in current_style.upper())
    if 'Dark'.upper() in current_style.upper():
        return True
    else:
        return False


def loadStylesheet():
    # Pega o tema atual do sistema
    app = QApplication.instance()
    current_style = app.style().objectName()

    # Verifica se existe a palavra dark no tema
    if 'Dark'.upper() in current_style.upper():
        path = theme_dark_path
    else:
        path = theme_light_path

    with open(path, 'r') as f:
        style = f.read()
    app.setStyleSheet(style)
