from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSettings, pyqtSignal
from zapzap.view.personalization_page import Ui_Personalization
from .tools import updateTextCheckBox
from gettext import gettext as _
import zapzap


class Personalization(QWidget, Ui_Personalization):

    emitUpdateTheme = pyqtSignal(str)
    emitDisableTrayIcon = pyqtSignal(bool)
    emitNotifications = pyqtSignal()

    themeDict = {'auto': 0, 'light': 1, 'dark': 2}
    iconDict = {'default': 0, 'symbolic_light': 1, 'symbolic_dark': 2}

    def __init__(self):
        super(Personalization, self).__init__()
        self.setupUi(self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)

        self.appThemeCBox.addItem(_("Automatic (System)"))
        self.appThemeCBox.addItem(_("Light style"))
        self.appThemeCBox.addItem(_("Dark style"))

        self.trayIconCBox.addItem(_("Default"))
        self.trayIconCBox.addItem(_("Symbolic light"))
        self.trayIconCBox.addItem(_("Symbolic dark"))

        self.disableTrayIcon.clicked.connect(self.setDisableTrayIcon)
        

        self.appThemeCBox.textActivated.connect(self.setTheme)
        self.trayIconCBox.textActivated.connect(self.setTray)

        self.load()

    def load(self):
        ## Appearance ##
        theme_mode = self.settings.value("system/theme", 'auto', str)
        self.appThemeCBox.setCurrentIndex(self.themeDict[theme_mode])

        ## Theme Icon ##
        theme_icon = self.settings.value(
            "notification/theme_tray", 'default', str)
        self.trayIconCBox.setCurrentIndex(self.iconDict[theme_icon])

        # Tray
        self.disableTrayIcon.setChecked(self.settings.value(
            "system/tray_icon", True, bool))  # tray_icon

        updateTextCheckBox(self.disableTrayIcon)

    def setTheme(self):
        c = self.appThemeCBox.currentIndex()
        theme = self.get_key(c, self.themeDict)
        
        self.settings.setValue("system/theme", theme)
        self.emitUpdateTheme.emit(theme)

    def setTray(self):
        c = self.trayIconCBox.currentIndex()
        theme = self.get_key(c, self.iconDict)

        self.settings.setValue("notification/theme_tray", theme)
        self.emitNotifications.emit()

    def get_key(self, val, my_dict):
        for key, value in my_dict.items():
            if val == value:
                return key

        return "There is no such Key"

    def setDisableTrayIcon(self):
        updateTextCheckBox(self.disableTrayIcon)
        self.settings.setValue("system/tray_icon",
                               self.disableTrayIcon.isChecked())
        self.emitDisableTrayIcon.emit(self.disableTrayIcon.isChecked())
