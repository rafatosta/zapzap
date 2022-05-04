from PyQt6.QtWidgets import QApplication

def isDarkTheme():
    app = QApplication.instance()
    current_style = app.style().objectName()
    return 'Dark'.upper() in current_style.upper()

