import os
import shutil
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSettings, pyqtSignal
from zapzap.controllers.user_container import UserContainer
from zapzap.controllers.settings import Settings
from zapzap.controllers.drawer import Drawer
from zapzap.model.user import UserDAO
from zapzap.view.home import Ui_Home
import zapzap


class Home(QWidget, Ui_Home):
    """
    The Home Class manages the user bar and users' pages.
    The sidebar consists of custom qpushbutton and pages within a QSTackedwidget, 
    both with the same position.
    """

    list = None

    # personalization
    emitUpdateTheme = pyqtSignal(str)
    emitDisableTrayIcon = pyqtSignal(bool)
    emitNotifications = pyqtSignal()

    # Quit
    emitQuit = pyqtSignal()

    # New chat
    emitNewChatAtNumber = pyqtSignal()

    def __init__(self):
        super(Home, self).__init__()
        self.setupUi(self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)

        self.loadUsers()
        self.loadActionsMenuBar()

        self.zapSettings = Settings()
        # Account
        self.zapSettings.emitDisableUser.connect(self.disableUserPage)
        self.zapSettings.emitDeleteUser.connect(self.delUserPage)
        self.zapSettings.emitEditUser.connect(self.editUserPage)
        self.zapSettings.emitNewtUser.connect(self.addNewUser)
        # Personalization (Atribuição inversa, pois todos os componentes já existem)
        self.emitUpdateTheme = self.zapSettings.emitUpdateTheme
        self.emitDisableTrayIcon = self.zapSettings.emitDisableTrayIcon
        self.emitNotifications = self.zapSettings.emitNotifications
        # Avanced
        self.zapSettings.emitHideSettingsBar.connect(self.activeSettingsBar)
        # Quit
        self.emitQuit = self.zapSettings.emitQuit
        self.zapSettings.emitCloseSettings.connect(self.openSettings)
        # Open Whatsapp Settings
        self.zapSettings.emitOpenSettingsWhatsapp.connect(
            self.openWhatsappSettings)
        # Update Pages
        self.zapSettings.emitUpdateProxyPage.connect(
            self.reloadAllPages)

        # Drawer for Settings window
        self.drawer = Drawer(self)
        self.drawer.maximum_width = self.width()
        self.drawer.raise_()
        self.drawer.stackedWidget.insertWidget(0, self.zapSettings)

        # At the end, update the shortcuts
        self.updateShortcuts()

    #### Accounts ####

    def resizeEvent(self, event):
        self.drawer.setFixedHeight(self.height() - self.drawer.pos().y())
        self.drawer.maximum_width = self.width()
        super().resizeEvent(event)

    def loadUsers(self):
        """Carries all users from the database"""
        self.list = UserDAO.select()
        for user in self.list:
            button = UserContainer(self, user)
            self.menu.addWidget(button)
            self.userStacked.addWidget(button.getBrowser())

        # Select default account
        self.menu.itemAt(0).widget().selected()

    def updateShortcuts(self):
        """Updates access shortcuts to users"""
        cont = 1
        for i in range(self.userStacked.count()):
            btn = self.menu.itemAt(i).widget()
            if btn.user.enable:
                btn.setShortcut(f'Ctrl+{cont}')
                cont += 1

        # Updates the description of the shortcuts in Account
        self.zapSettings.accountPage.updateUsersShortcuts()

        self.activeSettingsBar()

    #### MenuBar ####
    def loadActionsMenuBar(self):
        # Open Perfil
        self.btnHomePerfil.clicked.connect(self.openPerfil)

        self.btnHomeSetting.clicked.connect(self.openSettings)

        # New chat
        self.btnHomeNewChat.clicked.connect(self.newConversation)

        # New chat at phone number
        self.btnHomeNewChatPhone.clicked.connect(
            lambda: self.emitNewChatAtNumber.emit())

        # New Account
        def newAccount():
            from zapzap.model.user import UserDAO
            from zapzap.controllers.card_user import User
            from zapzap.theme.builder_icon import getNewIconSVG
            LIMITE_USERS = 9

            if self.menu.count() < LIMITE_USERS:
                # Cria o usuário
                user = User(
                    name='', icon=getNewIconSVG())
                # insere no banco de dados e recebe o user com o ID
                user = UserDAO.add(user)
                self.zapSettings.accountPage.updateListUser(user)
                self.addNewUser(user)
        self.btnHomeNewAccount.clicked.connect(newAccount)

    def activeSettingsBar(self):
        """Activate the menu only for more than one user"""
        if len(self.list) == 1 and self.settings.value(
                "system/hide_bar_users", False, bool):

            self.menuUsers.hide()
        else:
            # self.menu.itemAt(0).widget().selected()
            self.menuUsers.show()

    #### Settings ####
    def openSettings(self):
        """Open settings"""
        self.drawer.onToggled()

    def openDonations(self):
        self.openSettings()
        self.zapSettings.openDonations()

    #### Containers Whatsapp ####
    def setPage(self, browser):
        """Defines the page to be shown"""
        self.userStacked.setCurrentWidget(browser)

    def getUserContainer(self, idUser):
        """Take the container from the user ID"""
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            if btn.user.id == idUser:
                return btn, i
        return None

    def setFocusBrowser(self):
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.setFocusBrowser()

    def reloadPage(self):
        """Current page recharge"""
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.doReloadPage()
    
    def reloadAllPages(self):
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn = self.menu.itemAt(i).widget()
            btn.doReloadPage()

    def closeConversation(self, closeAll=False):
        if not self.drawer.isOpen:
            self.drawer.onToggled()
        elif closeAll:
            for i in range(self.menu.count()):
                btn = self.menu.itemAt(i).widget()
                btn.closeConversation()
        else:
            i = self.userStacked.currentIndex()
            btn = self.menu.itemAt(i).widget()
            btn.closeConversation()

    def openPerfil(self):
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.openPerfil()

    def openWhatsappSettings(self):
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.openWhatsappSettings()
        self.openSettings()

    def newConversation(self):
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.newConversation()

    def openChat(self, url):
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.openChat(url)

    #### CRUD Account ####

    def addNewUser(self, user):
        """Add new user to the list, in the container (menu button) and the page at Stacked"""
        self.list.append(user)
        button = UserContainer(self, user)
        self.menu.addWidget(button)
        self.userStacked.addWidget(button.getBrowser())

        self.updateShortcuts()

    def editUserPage(self, user):
        return_btn = self.getUserContainer(user.id)
        btn = return_btn[0]
        btn.setUser(user)

    def disableUserPage(self, user):
        """Disable user"""
        # If enabled, remove from stacked
        if user.enable:
            self.list.append(user)
            button = UserContainer(self, user)
            self.menu.addWidget(button)
            self.userStacked.addWidget(button.getBrowser())
        else:
            # Get UserContainer
            return_btn = self.getUserContainer(user.id)
            btn = return_btn[0]
            id_btn = return_btn[1]

            # Remove of userStacked
            self.userStacked.removeWidget(btn.getBrowser())

            # Remove icon of menu
            self.menu.itemAt(id_btn).widget().setParent(None)

            # Close browser
            btn.closeBrowser()

            # Update DB
            UserDAO.update(user)

            # Delete user list
            for u in self.list:
                if u.id == user.id:
                    self.list.remove(u)

        self.updateShortcuts()

    def delUserPage(self, user):
        """Delete user"""
        try:
            if user.enable:
                # Get UserContainer
                return_btn = self.getUserContainer(user.id)
                btn = return_btn[0]
                id_btn = return_btn[1]

                # Remove of userStacked
                self.userStacked.removeWidget(btn.browser)

                # Remove icon of menu
                self.menu.itemAt(id_btn).widget().setParent(None)

                # Close browser
                btn.closeBrowser()

            # Delete DB
            UserDAO.delete(user.id)

            # Delete user list
            for u in self.list:
                if u.id == user.id:
                    self.list.remove(u)

            # Delete QSettings
            qset = QSettings(zapzap.__appname__, zapzap.__appname__)
            qset.remove(f'{str(user.getId())}/notification')

            # Delete User Data
            path = os.path.join(zapzap.path_storage, str(user.id))
            shutil.rmtree(path, ignore_errors=True)
        except OSError as error:
            print(error)
            print("File path can not be removed")
        else:
            print("% s removed successfully" % path)
        finally:
            self.updateShortcuts()

    #### ZoomFactor ####

    def setZoomFactor(self, factor=None):
        """Current page zoom
            - Factor=None -> default (1.0).
            - factor:int -> Increases to the current value"""
        i = self.userStacked.currentIndex()
        btn = self.menu.itemAt(i).widget()
        btn.setZoomFactorPage(factor)

    #### SpellChecker ####

    def setSpellChecker(self, lang):
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn.setSpellChecker(lang)

    def disableSpellChecker(self, flag):
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn.disableSpellChecker(flag)

    #### Notifications ####

    def getSizeNotifications(self) -> int:
        """Sum the notifications of all users"""
        qtd = 0
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            qtd += btn.qtd
        return qtd

    #### Themes ####

    def resetStyle(self):
        """Restart the style of the user icons"""
        for i in reversed(range(self.menu.count())):
            ub = self.menu.itemAt(i).widget()
            ub.unselected()

    def setThemePages(self, theme):
        """Define or theme for all pages page"""
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn.setThemePage(theme)

    #### Save settings ####

    def saveSettings(self):
        """Save settings all users"""
        for i in range(self.menu.count()):
            btn = self.menu.itemAt(i).widget()
            btn.saveSettings()
