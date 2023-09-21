from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSettings, QSize, QUrl, QLocale, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QIcon
import zapzap
from zapzap.controllers.card_user import CardUser
from zapzap.model.user import User, UserDAO
from zapzap.services.portal_desktop import createDesktopFile
from gettext import gettext as _
from ..services.spellCheckLanguages import SpellCheckLanguages
from zapzap.theme.builder_icon import getImageQPixmap, getNewIconSVG

from zapzap.view.settings import Ui_Settings


class Settings(QWidget, Ui_Settings):

    LIMITE_USERS = 9

    emitDisableUser = pyqtSignal(User)
    emitDeleteUser = pyqtSignal(User)
    emitEditUser = pyqtSignal(User)
    emitNewtUser = pyqtSignal(User)

    emitSetSpellChecker = pyqtSignal(str)
    emitDisableSpellChecker = pyqtSignal(bool)

    emitNotifications = pyqtSignal()

    emitQuit = pyqtSignal()
    emitGoHome = pyqtSignal()

    emitKeepBackground = pyqtSignal(bool)
    emitDisableTrayIcon = pyqtSignal(bool)
    emitSetHideMenuBar = pyqtSignal()
    emitUpdateUIDecoration = pyqtSignal()
    emitUpdateTheme = pyqtSignal(str)

    def __init__(self):
        super(Settings, self).__init__()
        self.setupUi(self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.load()
        self.settingsActions()
        self.loadInfoHelp()
        self.loadDonations()
        self.loadUsers()
        self.loadSpellChecker()

        self.show_sound.setVisible(False)

        if zapzap.isFlatpak:
            self.wayland.setVisible(False)
            self.lineWayland.setVisible(False)

    def loadSpellChecker(self):
        def action():
            currentLanguage = self.comboSpellChecker.currentData()
            self.settings.setValue(
                "system/spellCheckLanguage", currentLanguage)
            self.emitSetSpellChecker.emit(currentLanguage)

        self.btnApply.clicked.connect(action)

        for chave, valor in SpellCheckLanguages.languages.items():
            self.comboSpellChecker.addItem(f'{_(valor)} ({chave})', chave)

        lang = self.settings.value(
            "system/spellCheckLanguage", QLocale.system().name(), str)

        try:
            sys_lang = SpellCheckLanguages.languages[lang]
        except:  # se não for um idioma suportado não fecha o app
            v = _("System Language")
            sys_lang = f'{v} (??)'
            self.comboSpellChecker.addItem(sys_lang, chave)

        index = self.comboSpellChecker.findData(lang)
        self.comboSpellChecker.setCurrentIndex(index)

    def loadUsers(self):
        """def clear():
            for i in reversed(range(self.usersList.count())):
                self.usersList.itemAt(i).widget().setParent(None)
        clear()"""
        list = UserDAO.select(False)
        for user in list:
            self.usersList.addWidget(self.getNewCardUser(user))

    def getNewCardUser(self, user) -> CardUser:
        card = CardUser(user)
        card.emitDisableUser = self.emitDisableUser
        card.emitDeleteUser = self.emitDeleteUser
        card.emitEditUser = self.emitEditUser
        return card

    def updateUsersShortcuts(self):
        count = 1
        for i in range(self.usersList.count()):
            card = self.usersList.itemAt(i).widget()
            if card.user.enable:
                card.key.setText(f'Ctrl+{count}')
                count += 1
            else:
                card.key.setText('')

        if count == self.LIMITE_USERS:
            self.label_limiteUser.show()
        else:

            self.label_limiteUser.hide()

    def loadDonations(self):
        self.btn_paypal.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/PayPal.png'))
        self.btn_paypal.setIconSize(QSize(250, 100))
        self.btn_paypal.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__paypal__)))

        self.btn_pix.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/pix.png'))
        self.btn_pix.setIconSize(QSize(250, 100))
        self.btn_pix.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__pix__)))

        self.btn_kofi.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/kofi.svg'))
        self.btn_kofi.setIconSize(QSize(250, 100))
        self.btn_kofi.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__kofi__)))

        self.btn_gitSponor.setIcon(
            QIcon(zapzap.abs_path+'/assets/icons/banners/sponsor.svg'))
        self.btn_gitSponor.setIconSize(QSize(250, 100))
        self.btn_gitSponor.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__githubSponor__)))

    def loadInfoHelp(self):
        self.version_app.setText(
            _(self.version_app.text()).format(id=zapzap.__version__))
        self.icon_app.setPixmap(getImageQPixmap())
        # actions
        self.btn_learn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__website__)))
        self.btn_changelog.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__releases__)))
        self.btn_report.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(zapzap.__bugreport__)))

    def settingsActions(self):
        # New User
        self.btnNewUser.clicked.connect(self.newUserbuttonClick)

        ## Menu left ##
        self.btn_home.clicked.connect(lambda: self.emitGoHome.emit())
        self.btn_system.clicked.connect(self.buttonClick)
        self.btn_appearance.clicked.connect(self.buttonClick)
        self.btn_notifications.clicked.connect(self.buttonClick)
        self.btn_donations.clicked.connect(self.buttonClick)
        self.btn_about.clicked.connect(self.buttonClick)
        self.btn_users.clicked.connect(self.buttonClick)
        self.btn_quit.clicked.connect(self.buttonClick)
        ## System ##
        self.start_system.clicked.connect(self.actionsSystemMenu)
        self.keepBackground.clicked.connect(self.actionsSystemMenu)
        self.disableTrayIcon.clicked.connect(self.actionsSystemMenu)
        self.menubar.clicked.connect(self.actionsSystemMenu)
        self.checkSpellChecker.clicked.connect(self.actionsSystemMenu)
        self.check_zap_window.clicked.connect(self.actionsSystemMenu)
        self.cb_maximize.clicked.connect(self.actionsSystemMenu)
        self.cb_minimize.clicked.connect(self.actionsSystemMenu)
        self.cb_positLeft.clicked.connect(self.actionsSystemMenu)

        self.wayland.clicked.connect(self.save)

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
        self.show_sound.clicked.connect(self.save)

        ## Set start page ##
        self.goPageHome()

    def newUserbuttonClick(self):
        if self.usersList.count() < self.LIMITE_USERS:
            # Cria o usuário
            user = User(
                name='', icon=getNewIconSVG())
            # insere no banco de dados e recebe o user com o ID
            user = UserDAO.add(user)
            # Insere  o card
            self.usersList.addWidget(self.getNewCardUser(user))
            # Informa a criação do usuário
            self.emitNewtUser.emit(user)

    def goPageHome(self):
        self.settings_stacked.setCurrentIndex(5)
        self.resetStyle('btn_users')
        self.btn_users.setStyleSheet(
            self.selectMenu(self.btn_users.styleSheet()))

    def goPageDonations(self):
        self.settings_stacked.setCurrentIndex(3)
        self.resetStyle('btn_donations')
        self.btn_donations.setStyleSheet(
            self.selectMenu(self.btn_donations.styleSheet()))

    def goPageHelp(self):
        self.settings_stacked.setCurrentIndex(4)
        self.resetStyle('btn_about')
        self.btn_about.setStyleSheet(
            self.selectMenu(self.btn_about.styleSheet()))

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)
        self.show_sound.setEnabled(s)

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
        self.emitNotifications.emit()

    def actionsRbAppearance(self):
        """ Actions by defining the appearance """
        if self.rb_system.isChecked():
            theme = 'auto'
        if self.rb_light.isChecked():
            theme = 'light'
        if self.rb_dark.isChecked():
            theme = 'dark'

        self.settings.setValue("system/theme", theme)
        self.emitUpdateTheme.emit(theme)

    def actionsSystemMenu(self):
        btn = self.sender()  # returns a pointer to the object that sent the signal
        btnName = btn.objectName()
        if btnName == 'start_system':
            # cria ou remove o arquivo
            createDesktopFile(bool(self.start_system.isChecked()))

        if btnName == 'keepBackground':
            self.emitKeepBackground.emit(self.keepBackground.isChecked())
        if btnName == 'disableTrayIcon':
            self.emitDisableTrayIcon.emit(self.disableTrayIcon.isChecked())
        if btnName == 'menubar':
            self.emitSetHideMenuBar.emit()
        if btnName == 'check_zap_window':
            self.frameZapWindow.setEnabled(self.check_zap_window.isChecked())
        if btnName == 'checkSpellChecker':
            self.frameSpellChecker.setEnabled(
                self.checkSpellChecker.isChecked())
            self.emitDisableSpellChecker.emit(
                self.checkSpellChecker.isChecked())

        self.save()
        self.emitUpdateUIDecoration.emit()

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

        if btnName == 'btn_donations':
            self.settings_stacked.setCurrentIndex(3)
            self.btn_donations.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_about':
            self.settings_stacked.setCurrentIndex(4)
            self.btn_about.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_users':
            self.settings_stacked.setCurrentIndex(5)
            self.btn_users.setStyleSheet(
                self.selectMenu(self.btn_system.styleSheet()))

        if btnName == 'btn_quit':
            self.emitQuit.emit()

    def load(self):
        """
        Load all settings
        """
        ## System ##
        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        self.start_system.setChecked(isStart_system)  # Start_system
        self.keepBackground.setChecked(self.settings.value(
            "system/keep_background", True, bool))  # keep_background

        self.disableTrayIcon.setChecked(self.settings.value(
            "system/tray_icon", True, bool))  # tray_icon

        self.wayland.setChecked(self.settings.value(
            "system/wayland", True, bool))

        # SpellChecker
        sc = self.settings.value(
            "system/spellCheckers", True, bool)
        self.checkSpellChecker.setChecked(sc)
        self.frameSpellChecker.setEnabled(sc)

        self.menubar.setChecked(self.settings.value(
            "main/hideMenuBar", False, bool))  # tray_icon
        zap_decor = self.settings.value(
            "system/zapzap_decoration", False, bool)
        self.check_zap_window.setChecked(zap_decor)
        self.frameZapWindow.setEnabled(self.check_zap_window.isChecked())
        self.cb_maximize.setChecked(self.settings.value(
            "system/winBtnMax", False, bool))
        self.cb_minimize.setChecked(self.settings.value(
            "system/winBtnMin", False, bool))
        self.cb_positLeft.setChecked(self.settings.value(
            "system/posBtnLeft", False, bool))

        ## Appearance ##
        theme_mode = self.settings.value("system/theme", 'auto', str)
        if theme_mode == 'auto':
            self.rb_system.setChecked(True)
        elif theme_mode == 'light':
            self.rb_light.setChecked(True)
        else:
            self.rb_dark.setChecked(True)

        ## Theme Icon ##
        theme_icon = self.settings.value(
            "notification/theme_tray", 'default', str)
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
        self.show_sound.setEnabled(isNotifyApp)
        # checked
        self.settings.setValue(
            'notification/app', self.notify_desktop.isChecked())
        self.show_photo.setChecked(self.settings.value(
            'notification/show_photo', True, bool))
        self.show_name.setChecked(self.settings.value(
            'notification/show_name', True, bool))
        self.show_msg.setChecked(self.settings.value(
            'notification/show_msg', True, bool))
        self.show_sound.setChecked(not self.settings.value(
            'notification/show_sound', False, bool))

    def save(self):
        """
        Save all settings
        """
        # System
        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())
        self.settings.setValue("system/keep_background",
                               self.keepBackground.isChecked())
        self.settings.setValue("system/tray_icon",
                               self.disableTrayIcon.isChecked())
        self.settings.setValue("main/hideMenuBar", self.menubar.isChecked())

        self.settings.setValue("system/spellCheckers",
                               self.checkSpellChecker.isChecked())

        self.settings.setValue("system/zapzap_decoration",
                               self.check_zap_window.isChecked())
        self.settings.setValue("system/winBtnMax",
                               self.cb_maximize.isChecked())
        self.settings.setValue("system/winBtnMin",
                               self.cb_minimize.isChecked())
        self.settings.setValue("system/posBtnLeft",
                               self.cb_positLeft.isChecked())

        self.settings.setValue("system/wayland",
                               self.wayland.isChecked())

        # Notifications
        self.settings.setValue('notification/app',
                               self.notify_desktop.isChecked())
        self.settings.setValue('notification/show_photo',
                               self.show_photo.isChecked())
        self.settings.setValue('notification/show_name',
                               self.show_name.isChecked())
        self.settings.setValue('notification/show_msg',
                               self.show_msg.isChecked())
        self.settings.setValue('notification/show_sound',
                               not self.show_sound.isChecked())

    # SELECT/DESELECT MENU
    # ///////////////////////////////////////////////////////////////
    # SELECT
    # MENU SELECTED STYLESHEET
    MENU_SELECTED_STYLESHEET = """
    border-bottom: 2px solid #00BD95;
    font: 13pt;
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
