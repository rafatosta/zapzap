from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSettings, QSize, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6 import uic
import zapzap
from zapzap.services.portal_desktop import createDesktop, removeDesktop


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        uic.loadUi(zapzap.abs_path+'/view/settings.ui', self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.mainWindow = parent
        self.load()
        self.settingsActions()
        self.loadInfoHelp()

    def loadInfoHelp(self):
        self.icon_app.setPixmap(zapzap.getIconTray().pixmap(QSize(50, 50)))
        self.name_app.setText(zapzap.__appname__)
        self.version_app.setText(
            f'Version {zapzap.__version__} (Official compilation)')
        self.desc_app.setText(
            'An unofficial WhatsApp desktop application written in Pyqt6 + PyQt6-WebEngine.')
        self.name_app2.setText(zapzap.__appname__)

        # actions
        self.btn_learn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__website__)))
        self.btn_changelog.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__releases__)))
        self.btn_report.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__bugreport__)))
        self.btn_buy.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__buycoffe__)))

    def settingsActions(self):
        ## Menu left ##
        self.btn_home.clicked.connect(
            lambda: self.mainWindow.main_stacked.setCurrentIndex(0))
        self.btn_system.clicked.connect(self.buttonClick)
        self.btn_appearance.clicked.connect(self.buttonClick)
        self.btn_notifications.clicked.connect(self.buttonClick)
        self.btn_about.clicked.connect(self.buttonClick)
        ## System ##
        self.start_system.clicked.connect(self.actionsSystemMenu)
        self.start_hide.clicked.connect(self.actionsSystemMenu)
        self.keepBackground.clicked.connect(self.actionsSystemMenu)
        self.disableTrayIcon.clicked.connect(self.actionsSystemMenu)
        self.menubar.clicked.connect(self.actionsSystemMenu)

        ## Appearance ##
        self.rb_system.clicked.connect(self.actionsRbAppearance)
        self.rb_light.clicked.connect(self.actionsRbAppearance)
        self.rb_dark.clicked.connect(self.actionsRbAppearance)

        self.rb_tray_default.clicked.connect(self.actionsRbTray)
        self.rb_tray_light.clicked.connect(self.actionsRbTray)
        self.rb_tray_dark.clicked.connect(self.actionsRbTray)

        ## Notifications ##
        self.notify_desktop.stateChanged.connect(self.state_notify_desktop)
        self.show_photo.clicked.connect(self.save)
        self.show_name.clicked.connect(self.save)
        self.show_msg.clicked.connect(self.save)

        ## Set start page ##
        self.settings_stacked.setCurrentIndex(0)
        self.btn_system.setStyleSheet(
            self.selectMenu(self.btn_system.styleSheet()))

    def goPageHome(self):
        self.settings_stacked.setCurrentIndex(0)
        self.resetStyle('btn_system')
        self.btn_system.setStyleSheet(
            self.selectMenu(self.btn_system.styleSheet()))

    def goPageHelp(self):
        self.settings_stacked.setCurrentIndex(3)
        self.resetStyle('btn_about')
        self.btn_about.setStyleSheet(
            self.selectMenu(self.btn_about.styleSheet()))

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)

        self.save()

    def actionsRbTray(self):
        theme = 'default'
        if self.rb_tray_default.isChecked():
            """default"""

        if self.rb_tray_light.isChecked():  # icone preto
            theme = 'symbolic_light'

        if self.rb_tray_dark.isChecked():  # icone branco
            theme = 'symbolic_dark'

        self.settings.setValue("notification/theme_tray", theme)
        self.mainWindow.browser.title_changed(self.mainWindow.windowTitle())

    def actionsRbAppearance(self):
        theme = 'auto'
        if self.rb_system.isChecked():
            """Ativa o contador"""
            self.mainWindow.current_theme = -1
            self.mainWindow.timer.start()
        if self.rb_light.isChecked():
            theme = 'light'
            """Desativa o contador e ativa o light"""
            self.mainWindow.timer.stop()
            self.mainWindow.setThemeApp(False)
        if self.rb_dark.isChecked():
            theme = 'dark'
            """Desativa o contador e ativa o dark"""
            self.mainWindow.timer.stop()
            self.mainWindow.setThemeApp(True)

        self.settings.setValue("system/theme", theme)

    def actionsSystemMenu(self):
        btn = self.sender()  # returns a pointer to the object that sent the signal
        btnName = btn.objectName()
        if btnName == 'start_system':
            self.start_hide.setEnabled(self.start_system.isChecked())
            # cria ou remove o arquivo
            if bool(self.start_system.isChecked()):
                createDesktop()
            else:
                removeDesktop()
        if btnName == 'keepBackground':
            self.mainWindow.actionHide_on_close.setChecked(
                self.keepBackground.isChecked())
        if btnName == 'disableTrayIcon':
            self.mainWindow.tray.setVisible(
                not self.disableTrayIcon.isChecked())
        if btnName == 'menubar':
            self.mainWindow.setHideMenuBar()

        self.save()

    def buttonClick(self):
        btn = self.sender()  # returns a pointer to the object that sent the signal
        btnName = btn.objectName()
        # print(btnName)

        self.resetStyle(btnName)
        if btnName == 'btn_system':
            self.settings_stacked.setCurrentIndex(0)
            self.btn_system.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_appearance':
            self.settings_stacked.setCurrentIndex(1)
            self.btn_appearance.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_notifications':
            self.settings_stacked.setCurrentIndex(2)
            self.btn_notifications.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_about':
            self.settings_stacked.setCurrentIndex(3)
            self.btn_about.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

    def load(self):
        """
        Load all settings
        """
        ## System ##
        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        self.start_system.setChecked(isStart_system)  # Start_system
        self.start_hide.setEnabled(isStart_system)  # Enable Start Hide
        self.start_hide.setChecked(self.settings.value(
            "system/start_hide", False, bool))  # Start_hide
        self.keepBackground.setChecked(self.settings.value(
            "system/keep_background", True, bool))  # keep_background

        self.disableTrayIcon.setChecked(not self.settings.value(
            "system/tray_icon", True, bool))  # tray_icon

        self.menubar.setChecked(self.settings.value(
            "main/hideMenuBar", False, bool))  # tray_icon

        ## Appearance ##
        theme_mode = self.settings.value("system/theme", 'auto', str)
        if theme_mode == 'auto':
            self.rb_system.setChecked(True)
        elif theme_mode == 'light':
            self.rb_light.setChecked(True)
        else:
            self.rb_dark.setChecked(True)

        ## Theme Icon ##
        theme_icon = self.mainWindow.settings.value(
            "notification/theme_tray", 'default', str)
        print()
        if theme_icon == 'default':
            self.rb_tray_default.setChecked(True)
        elif theme_icon == 'symbolic_light':
            self.rb_tray_light.setChecked(True)
        else:
            self.rb_tray_dark.setChecked(True)

        ## Notifications ##
        isNotifyApp = self.settings.value("notification/app", True, bool)
        self.notify_desktop.setChecked(isNotifyApp)
        # enable ou disable
        self.show_photo.setEnabled(isNotifyApp)
        self.show_name.setEnabled(isNotifyApp)
        self.show_msg.setEnabled(isNotifyApp)
        # checked
        self.settings.setValue(
            'notification/app', self.notify_desktop.isChecked())
        self.show_photo.setChecked(self.settings.value(
            'notification/show_photo', True, bool))
        self.show_name.setChecked(self.settings.value(
            'notification/show_name', True, bool))
        self.show_msg.setChecked(self.settings.value(
            'notification/show_msg', True, bool))

    def save(self):
        """
        Save all settings
        """
        # System
        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())
        self.settings.setValue("system/start_hide",
                               self.start_hide.isChecked())
        self.settings.setValue("system/keep_background",
                               self.keepBackground.isChecked())
        self.settings.setValue("system/tray_icon",
                               not self.disableTrayIcon.isChecked())
        self.settings.setValue("main/hideMenuBar", self.menubar.isChecked())

        # Notifications
        self.settings.setValue('notification/app',
                               self.notify_desktop.isChecked())
        self.settings.setValue('notification/show_photo',
                               self.show_photo.isChecked())
        self.settings.setValue('notification/show_name',
                               self.show_name.isChecked())
        self.settings.setValue('notification/show_msg',
                               self.show_msg.isChecked())

    # SELECT/DESELECT MENU
    # ///////////////////////////////////////////////////////////////
    # SELECT
    # MENU SELECTED STYLESHEET
    MENU_SELECTED_STYLESHEET = """
    background-color: #00BD95;
    border-color: #00BD95;
    font-weight: bold;
    """

    def selectMenu(self, getStyle):
        select = getStyle + self.MENU_SELECTED_STYLESHEET
        return select

    # DESELECT
    def deselectMenu(self, getStyle):
        deselect = getStyle.replace(self.MENU_SELECTED_STYLESHEET, "")
        return deselect

    # RESET SELECTION
    def resetStyle(self, widget):
        for w in self.menu.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(self.deselectMenu(w.styleSheet()))
