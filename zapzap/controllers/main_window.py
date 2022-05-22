from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon
from PyQt6.QtGui import QMoveEvent, QAction, QActionGroup, QKeySequence
from PyQt6.QtCore import QSettings, QByteArray
from PyQt6 import uic
import zapzap
from zapzap.controllers.about import About
from zapzap.controllers.main_window_components.menu_bar import MenuBar
from zapzap.controllers.main_window_components.tray_icon import TrayIcon
from zapzap.controllers.quick_switch import QuickSwitch
from zapzap.controllers.settings import Settings
from zapzap.controllers.users import Users
from zapzap.engine.browser import Browser


class MainWindow(QMainWindow):

    openDialog = None
    isFullScreen = False
    isHideMenuBar = False
    list_browser = []

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        uic.loadUi(zapzap.abs_path+'/view/main_window.ui', self)
        self.app = parent
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.users_sgs = QSettings(zapzap.__appname__, 'users')

        MenuBar(self)
        self.tray = TrayIcon(self)

        self.loadUsers()

    def loadUsers(self):
        """
        Upload all users and start whatsapp sessions
        """
        self.users_sgs.beginGroup("users")
        keys = self.users_sgs.allKeys()
        # If the list is empty, it starts with the default user
        if not len(keys) > 0:
            self.users_sgs.setValue(
                "storage-whats", {'storageName': 'storage-whats', 'name': 'Whatsapp'})
            keys = self.users_sgs.allKeys()
        """
        For each user create:
            + The Browser: Page for whatsapp
            + Action menu
        """
        # creating a action group
        for id, u in enumerate(keys):
            # Browser
            b = Browser(self.users_sgs.value(u, dict), self)
            b.setZoomFactor(self.settings.value(
                "browser/zoomFactor", 1.0, float))
            b.doReload()
            self.list_browser.append(b)
            # QAction
            action = QAction(self.users_sgs.value(u, dict)['name'], self)
            action.setShortcut(QKeySequence(f'Ctrl+{id+1}'))
            action.triggered.connect(
                lambda checked, index=id: self.setStackedWidgetPage(index))
            self.menuUsers.addAction(action)
            self.stackedWidget.addWidget(b)
        self.users_sgs.endGroup()  # encerra o grupo (não pode esquecer)

    def setStackedWidgetPage(self, id):
        print('Set :', id)
        self.stackedWidget.setCurrentIndex(id)

    def reload_Service(self):
        print('f5')
        # é possível modificar/acessar mantendo uma lista
        for b in self.list_browser:
            b.whats.setTheme(True)

    def openSettingsDialog(self):
        pass
        #self.openDialog = Users()  # Settings()
        #self.openDialog.show()

    def openNewUserDialog(self):
        self.openDialog = Users()
        self.openDialog.show()

    def openAbout_Zapzap(self):
        self.openDialog = About(self)
        self.openDialog.show()

    def moveEvent(self, a0: QMoveEvent) -> None:
        if self.openDialog != None:
            self.openDialog.centerPos()
        return super().moveEvent(a0)

    def loadSettings(self):
        """
        Load the settings
        """
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
        # System start
        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        isStart_hide = self.settings.value("system/start_hide", False, bool)
        if isStart_system and isStart_hide:
            self.hide()
        else:
            self.show()

    def quit(self):
        """
        Close window.
        """
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.hide()
        self.app.quit()

    def closeEvent(self, event):
        """
        Override the window close event.
        Save window dimensions and check if it should be hidden or closed
        """
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())

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
        self.loadSettings()
        if self.app.activeWindow() != None:  # Se a janela estiver em foco será escondida
            self.hide()
        else:  # Caso não esteja, será mostrada
            self.show()
            self.app.activateWindow()

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
        """
        Hide/Show MenuBar
        """
        if self.isHideMenuBar:
            self.menubar.setMaximumHeight(0)
        else:
            # default size for qt designer
            self.menubar.setMaximumHeight(16777215)

        self.settings.setValue("main/hideMenuBar", self.isHideMenuBar)
        self.isHideMenuBar = not self.isHideMenuBar

    def open_Quick_Switch(self):
        """
        Open QuickSwitch
        """
        self.openDialog = QuickSwitch()
        self.openDialog.show()

    def updateNotificationIcon(self):
        """
        Updates the tray icon depending on the amount of pending notifications
        """
        n = 0
        for b in self.list_browser:
            n += b.numberNotifications
        self.tray.showIconNotification(n)
