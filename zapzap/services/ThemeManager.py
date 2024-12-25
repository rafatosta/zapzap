from PyQt6.QtCore import QTimer
from PyQt6.QtDBus import QDBusInterface
from enum import Enum

class ThemeManager:
    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    def __init__(self):
        self.current_theme = ThemeManager.Type.Auto
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 second interval for system theme checks
        self.timer.timeout.connect(self.syncThemeSys)
    
    def syncThemeSys(self):
        """Check the current system theme and apply it."""
        theme = self.getSystemTheme()
        print(theme)
        if self.current_theme != theme:
            self.current_theme = theme
            self.notifyThemeChange()

    def setTheme(self, theme):
        """Set the theme based on user choice."""
        if theme == ThemeManager.Type.Auto:
            self.timer.start()
        else:
            self.timer.stop()
            self.current_theme = theme
            self.notifyThemeChange()

    def notifyThemeChange(self):
        """Notify that the theme has changed."""
        if self.current_theme == ThemeManager.Type.Light:
            self.applyLightTheme()
        elif self.current_theme == ThemeManager.Type.Dark:
            self.applyDarkTheme()

    def applyLightTheme(self):
        print("""Apply the light theme.""")
        # Implement the light theme style logic here
        

    def applyDarkTheme(self):
        print("""Apply the dark theme.""")
        # Implement the dark theme style logic here
        

    def getCurrentTheme(self):
        """Get the current theme."""
        return self.current_theme

    def getSystemTheme(self):
        """Available color schemes:
        - 0: No preference (True)
        - 1: Prefer dark appearance (False)
        - 2: Prefer light appearance (True)
        """
        try:
            name = "org.freedesktop.portal.Desktop"
            path = "/org/freedesktop/portal/desktop"
            interface = "org.freedesktop.portal.Settings"

            smp = QDBusInterface(name, path, interface)
            msg = smp.call('Read', "org.freedesktop.appearance", 'color-scheme')
            color_scheme = msg.arguments()[0]
            return 'light' if (color_scheme == 0) or color_scheme == 2 else 'dark'
        except Exception:
            return 'light'
