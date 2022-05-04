from PyQt6.QtWidgets import QApplication

def isDarkTheme():
    app = QApplication.instance()
    current_style = app.style().objectName()
    print(current_style, 'Dark'.upper() in current_style.upper() )
    return 'Dark'.upper() in current_style.upper()

