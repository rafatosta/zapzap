from PyQt6.QtCore import QTimer
from PyQt6.QtDBus import QDBusInterface
from enum import Enum

from zapzap.services.SettingsManager import SettingsManager


class ThemeManager:
    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.current_theme = SettingsManager.get(
                "system/theme", ThemeManager.Type.Auto
            )
            self.timer = QTimer()
            self.timer.setInterval(1000)  # Check system theme every 1 second
            self.timer.timeout.connect(self.syncThemeSys)

    @staticmethod
    def instance():
        """Get the singleton instance of ThemeManager."""
        if ThemeManager._instance is None:
            ThemeManager()
        return ThemeManager._instance

    @staticmethod
    def start():
        """Start the ThemeManager and apply the theme from settings."""
        instance = ThemeManager.instance()
        if instance.current_theme == ThemeManager.Type.Auto:
            instance.timer.start()
            instance.syncThemeSys()  # Synchronize with system theme
        else:
            instance.notifyThemeChange()

    @staticmethod
    def setTheme(theme: Type):
        """Set the theme based on user choice."""
        instance = ThemeManager.instance()
        if theme == ThemeManager.Type.Auto:
            instance.timer.start()
        else:
            instance.timer.stop()
            instance.current_theme = theme
            instance.notifyThemeChange()

        # Save the theme type
        SettingsManager.set("system/theme", theme.value)

    @staticmethod
    def getCurrentTheme():
        """Get the current theme."""
        return ThemeManager.instance().current_theme

    def syncThemeSys(self):
        """Check the current system theme and apply it."""
        theme = self.getSystemTheme()
        if self.current_theme != theme:
            self.current_theme = theme
            self.notifyThemeChange()

    def notifyThemeChange(self):
        """Notify that the theme has changed."""
        if self.current_theme == ThemeManager.Type.Light:
            self.applyLightTheme()
        elif self.current_theme == ThemeManager.Type.Dark:
            self.applyDarkTheme()

    def applyLightTheme(self):
        """Apply the light theme."""
        print("Applying light theme...")
        # Implement the light theme style logic here

    def applyDarkTheme(self):
        """Apply the dark theme."""
        print("Applying dark theme...")
        # Implement the dark theme style logic here

    def getSystemTheme(self) -> Type:
        """
        Determine the system theme using D-Bus interface.
        Available color schemes:
        - 0: No preference (default to light)
        - 1: Prefer dark appearance
        - 2: Prefer light appearance
        """
        try:
            name = "org.freedesktop.portal.Desktop"
            path = "/org/freedesktop/portal/desktop"
            interface = "org.freedesktop.portal.Settings"

            smp = QDBusInterface(name, path, interface)
            msg = smp.call(
                "Read", "org.freedesktop.appearance", "color-scheme")
            color_scheme = msg.arguments()[0]

            if color_scheme == 1:
                return ThemeManager.Type.Dark
            return ThemeManager.Type.Light
        except Exception as e:
            print(f"Error getting system theme: {e}")
            return ThemeManager.Type.Light
