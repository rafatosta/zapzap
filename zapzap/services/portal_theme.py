from zapzap import theme_light_path, theme_dark_path
from PyQt6.QtWidgets import QApplication

"""def loadStylesheet(app):
    current_style = app.style().objectName()
    print(current_style, '<<<<')
    # Verifica se existe a palavra dark no tema
    if 'Dark'.upper() in current_style.upper():
        path = theme_dark_path
    else:
        path = theme_light_path

    with open(path, 'r') as f:
        style = f.read()
    app.setStyleSheet(style)"""


def isDarkTheme():
    app = QApplication.instance()
    current_style = app.style().objectName()
    print(current_style, 'Dark'.upper() in current_style.upper() )
    return 'Dark'.upper() in current_style.upper()


def loadStylesheet():
    app = QApplication.instance()
    current_style = app.style().objectName()
    print('>>>', current_style)
    print(app.style().metaObject().className())
    if 'Dark'.upper() in current_style.upper():
        path = theme_dark_path
    else:
        path = theme_light_path

    with open(path, 'r') as f:
        style = f.read()
    app.setStyleSheet(style)
