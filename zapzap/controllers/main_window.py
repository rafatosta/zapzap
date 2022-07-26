from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon
from PyQt6.QtCore import QSettings, QByteArray, QTimer
#from PyQt6 import uic
import zapzap
from zapzap.theme.zap_themes import getThemeDark, getThemeLight
from zapzap.controllers.main_window_components.menu_bar import MenuBar
from zapzap.controllers.main_window_components.tray_icon import TrayIcon
from zapzap.controllers.main_window_decoration.ui_decoration import UIDecoration
from zapzap.controllers.settings import Settings
from zapzap.engine.browser import Browser
from zapzap.services.dbus_theme import get_system_theme
from gettext import gettext as _

from zapzap.view.main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    isFullScreen = False
    isHideMenuBar = False
    list_browser = []  # remover isso depois
    container_list = []

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        #uic.loadUi(zapzap.abs_path+'/view/main_window.ui', self)
        self.app = parent
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.scd = None
        # create menu bar
        MenuBar(self)
        self.tray = TrayIcon(self)

        # create webengine for whatsapp page and insert in page zero
        self.browser = Browser(self)
        self.browser.setZoomFactor(self.settings.value(
            "browser/zoomFactor", 1.0, float))  # Reset user defined zoom (1.0 by default)
        # Refreshing the page avoids the outdated user-agent issue (still happens sometimes)
        self.browser.doReload()
        self.main_stacked.insertWidget(0, self.browser)

        # create panel settings and insert page one
        self.zapSettings = Settings(self)
        self.main_stacked.insertWidget(1, self.zapSettings)

        # timer for system theme change check (check in 1s)
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.current_theme = -1

        self.setZapDecoration()


    def setZapDecoration(self):
        self.headbar.hide()
        if self.settings.value("system/zap_decoration", True, bool):
            self.scd = UIDecoration(self)

    def recurring_timer(self):
        """ Check the current system theme and apply it in the app """
        theme = get_system_theme()
        if self.current_theme != theme:
            self.current_theme = theme
            self.setThemeApp(self.current_theme)

    def setThemeApp(self, isNight_mode):
        """"Apply the theme in the APP
            isNight_mode: boll
        """
        if isNight_mode:
            self.app.setStyleSheet(getThemeDark())
        else:
            self.app.setStyleSheet(getThemeLight())

        # Apply equivalent theme on whatsapp page
        self.browser.whats.setTheme(isNight_mode)

    def reload_Service(self):
        """Refreshing the page"""
        self.browser.doReload()

    def openSettings(self):
        """Open settings"""
        if self.main_stacked.currentIndex() == 1:
            self.main_stacked.setCurrentIndex(0)
        else:
            self.main_stacked.setCurrentIndex(1)
            self.zapSettings.goPageHome()

    def openDonations(self):
        """Open settings"""
        self.main_stacked.setCurrentIndex(1)
        self.zapSettings.goPageDonations()

    def openAbout_Zapzap(self):
        """Open About"""
        self.main_stacked.setCurrentIndex(1)
        self.zapSettings.goPageHelp()

    def loadSettings(self):
        """
        Load the settings
        """
        # Theme App
        theme_mode = self.settings.value("system/theme", 'auto', str)
        if theme_mode == 'auto':
            self.setThemeApp(get_system_theme())
            self.timer.start()
        elif theme_mode == 'light':
            self.setThemeApp(False)
        else:
            self.setThemeApp(True)
        # MenuBar
        self.isHideMenuBar = self.settings.value(
            "main/hideMenuBar", False, bool)
        self.setHideMenuBar()
        # keep_background
        self.actionHide_on_close.setChecked(self.settings.value(
            "system/keep_background", True, bool))
        # Window State
        self.restoreGeometry(self.settings.value(
            "main/geometry", QByteArray()))
        self.restoreState(self.settings.value(
            "main/windowState", QByteArray()))

    def quit(self):
        """
        Close window.
        """
        self.settings.setValue("browser/zoomFactor", self.browser.zoomFactor())
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.hide()
        self.app.quit()

    def closeEvent(self, event):
        """
        Override the window close event.
        Save window dimensions and check if it should be hidden or closed
        """
        self.settings.setValue("browser/zoomFactor", self.browser.zoomFactor())
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.timer.stop()
        if self.settings.value(
                "system/keep_background", True, bool):
            self.hide()
            event.ignore()

    def onTrayIconActivated(self, reason):
        """
        wind to show and hide the window with just two click or middle button on the tray icon. 
        One click opens the menu.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.on_show()
            self.app.activateWindow()

    def on_show(self):
        """
        Opening the system tray web app.
        """
        if self.app.activeWindow() != None:  # Se a janela estiver em foco será escondida
            self.hide()
        else:  # Caso não esteja, será mostrada
            self.show()
            self.app.activateWindow()
            self.main_stacked.setCurrentIndex(0)

    def setDefault_size_page(self):
        """Reset user defined zoom (1.0 by default)"""
        self.browser.setZoomFactor(1.0)

    def zoomIn(self):
        """Zoom in"""
        self.browser.setZoomFactor(self.browser.zoomFactor()+0.1)

    def zoomOut(self):
        """zoom out"""
        self.browser.setZoomFactor(self.browser.zoomFactor()-0.1)

    def setFullSreen(self):
        """
        Full Screen Window
        """
        if not self.isFullScreen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.isFullScreen = not self.isFullScreen

    def setHideMenuBar(self):
        if self.settings.value("system/zap_decoration", True, bool):
            self.menubar.setMaximumHeight(0)
        else:
            """
            Hide/Show MenuBar
            """
            if self.isHideMenuBar:
                self.menubar.setMaximumHeight(0)
            else:
                # default size for qt designer
                self.menubar.setMaximumHeight(16777215)

            self.settings.setValue("main/hideMenuBar", self.isHideMenuBar)
            self.zapSettings.menubar.setChecked(self.isHideMenuBar)
            self.isHideMenuBar = not self.isHideMenuBar
