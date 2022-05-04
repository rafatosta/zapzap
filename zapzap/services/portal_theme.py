
from zapzap import theme_light_path, theme_dark_path


def loadStylesheet(app):
    current_style = app.style().objectName()
    print(current_style, '<<<<')
    # Verifica se existe a palavra dark no tema
    if 'Dark'.upper() in current_style.upper():
        path = theme_dark_path
    else:
        path = theme_light_path

    with open(path, 'r') as f:
        style = f.read()
    app.setStyleSheet(style)
