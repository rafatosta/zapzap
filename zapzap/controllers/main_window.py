from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon
from PyQt6.QtCore import QSettings, QByteArray, QTimer
from PyQt6.QtGui import QIcon
from zapzap.controllers.open_chat_popup import OpenChatPopup
from zapzap.theme.zap_themes import getThemeDark, getThemeLight
from zapzap.controllers.main_window_components.tray_icon import TrayIcon
from zapzap.controllers.home import Home
from zapzap.controllers.qtoaster_donation import QtoasterDonation
from zapzap.services.dbus_theme import getSystemTheme
import zapzap
from gettext import gettext as _
from zapzap.view.main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    isFullScreen = False
    isHideMenuBar = False

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.app = parent
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.scd = None

        self.setWindowIcon(
            QIcon(zapzap.abs_path+'/assets/icons/tray/default_normal.svg'))

        # Object responsible for managing the tray icon
        self.tray = TrayIcon(self)

        # Home page
        self.zapHome = Home()
        self.zapHome.emitUpdateTheme.connect(self.setThemeApp)
        self.zapHome.emitDisableTrayIcon.connect(self.tray.setVisible)
        self.zapHome.emitNotifications.connect(self.emitNotifications)
        self.zapHome.emitQuit.connect(lambda x=None: self.closeEvent(x))
        self.zapHome.emitNewChatAtNumber.connect(self.openNewChatAtNumber)

        # hide menu bar
        self.menubar.setMaximumHeight(0)
        self.loadActionsMenuBar()

        self.setCentralWidget(self.zapHome)

        # timer for system theme change check (check in 1s)
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.syncThemeSys)
        self.current_theme = -1
        if self.settings.value(
                "system/donation_message", True, bool):
            QtoasterDonation.showMessage(parent=self)

    #### Donation ####
    def openDonations(self):
        self.zapHome.openDonations()

    #### MenuBar actions ####

    def loadActionsMenuBar(self):
        # File
        self.actionSettings.triggered.connect(
            self.openSettings)
        self.actionQuit.triggered.connect(
            lambda x=None: self.closeEvent(x))
        self.actionHide.triggered.connect(lambda: self.hide())

        # View
        self.actionReload_Service.triggered.connect(
            self.zapHome.reloadPage)
        self.actionDefault_size_page.triggered.connect(
            lambda: self.zapHome.setZoomFactor(None))
        self.actionToggle_Full_Screen.triggered.connect(
            self.setFullSreen)
        self.actionZoomIn.triggered.connect(
            lambda: self.zapHome.setZoomFactor(+0.1))
        self.actionZoomOut.triggered.connect(
            lambda: self.zapHome.setZoomFactor(-0.1))
        

        # Chat
        self.actionOpen_new_chat.triggered.connect(
            self.openNewChatAtNumber)

    def openSettings(self, isOpen):
        """Open settings"""
        self.zapHome.openSettings()

    def setFullSreen(self):
        """Full Screen Window"""
        if not self.isFullScreen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.isFullScreen = not self.isFullScreen

    def openNewChatAtNumber(self):
        """Create new chat from a phone number"""
        dialog = OpenChatPopup(self)
        r = dialog.exec_()
        if r == 1:
            number = dialog.numberPhone.text()
            if number != "":
                url = "https://api.whatsapp.com/send?phone="+number
                self.zapHome.openChat(url)

    #### Load and Save Settings for window ####

    def loadSettings(self):
        """
        Load the settings
        """
        # Theme App mode
        theme_mode = self.settings.value("system/theme", 'auto', str)
        self.setThemeApp(theme_mode)

        # Window State
        self.restoreGeometry(self.settings.value(
            "main/geometry", QByteArray()))
        self.restoreState(self.settings.value(
            "main/windowState", QByteArray()))

    def saveSettings(self):
        """Save Settings"""
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        # Warns the Home so that users save their settings
        self.zapHome.saveSettings()

    #### Window events ####

    def closeEvent(self, event):
        """
            Override the window close event.
            Save window dimensions and check if it should be hidden or closed
        """
        self.saveSettings()
        isBack = self.settings.value("system/keep_background", True, bool)
        if isBack and event:  # Hide app on close window
            if not self.zapHome.drawer.isOpen:
                self.zapHome.drawer.onToggled()
            self.zapHome.closeConversation(closeAll=True)
            self.hide()
            event.ignore()
        else:  # Quit app on close window
            self.hide()
            self.app.quit()

    def on_show(self):
        """
        Opening the system tray web app.
        """
        if self.app.activeWindow() != None:  # Se a janela estiver em foco será escondida
            self.saveSettings()
            self.hide()
        else:  # Caso não esteja, será mostrada
            self.loadSettings()
            self.show()
            self.raise_()
            self.app.activateWindow()

    def emitNotifications(self):
        """The notifications of all users to the tray"""
        qtd = self.zapHome.getSizeNotifications()

        if qtd > 0:
            self.setWindowTitle(zapzap.__appname__+" ("+str(qtd)+")")
        else:
            self.setWindowTitle(zapzap.__appname__)

        self.tray.showIconNotification(qtd)

    #### Tray icon ####

    def openTraySettings(self):
        """Opens the settings from the tray"""
        if self.app.activeWindow() == None:  # Se a janela estiver em foco será escondida
            self.show()
            self.app.activateWindow()

        self.zapHome.openSettings()

    def onTrayIconActivated(self, reason):
        """
        wind to show and hide the window with just two click or middle button on the tray icon. 
        One click opens the menu.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.on_show()

    #### Theme ####
    def syncThemeSys(self):
        """ Check the current system theme and apply it in the app """
        theme = getSystemTheme()
        if self.current_theme != theme:
            self.current_theme = theme
            self.setThemeApp('auto')

    def setThemeApp(self, theme):
        """" Apply the theme in the APP """
        if theme == "auto":
            theme = getSystemTheme()
            self.timer.start()
        else:
            self.timer.stop()

        if theme == "light":
            self.app.setStyleSheet(getThemeLight())
            self.zapHome.setThemePages(theme)
        elif theme == "dark":
            self.app.setStyleSheet(getThemeDark())
            self.zapHome.setThemePages(theme)

    #### External events ####

    def xdgOpenChat(self, url):
        """Open chat by clicking on a notification"""
        self.zapHome.openChat(url)
