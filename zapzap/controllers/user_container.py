from PyQt6.QtWidgets import QPushButton, QApplication
from PyQt6.QtCore import QSize
from zapzap.model.user import UserDAO
from zapzap.theme.builder_icon import getImageQIcon
from zapzap.engine.browser import Browser


class UserContainer(QPushButton):

    isSelected = False

    styleSheet_normal = """
    QPushButton {	
       qproperty-iconSize: 25px;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding:2px;
    }
    """

    styleSheet_hover = """
    QPushButton {	
       qproperty-iconSize: 40px;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding:2px;
    }
    """

    def __init__(self, parent=None, user=None):
        super(UserContainer, self).__init__()
        self.user = user
        self.home = parent

        self.qtd = 0

        self.setFlat(True)
        self.setMinimumSize(QSize(40, 40))
        self.setMaximumSize(QSize(40, 40))

        self.browser = Browser(user.id, self)
        self.browser.setZoomFactor(user.zoomFactor)
        self.browser.doReload()

        self.setToolTip(self.user.name)
        self.setIcon(getImageQIcon(svg_str=user.icon))
        self.setStyleSheet(self.styleSheet_normal)

        self.clicked.connect(self.click)

    def showIconNotification(self, qtd):
        self.qtd = qtd
        self.setIcon(getImageQIcon(svg_str=self.user.icon, qtd=qtd))
        mainWindow = QApplication.instance().getWindow()
        mainWindow.emitNotifications()
        self.setToolTip(f'{self.user.name} ({self.qtd})' if self.qtd >
                        0 else self.user.name)

    def click(self):
        self.home.resetStyle()
        self.home.setPage(self.browser)
        self.selected()

    def setUser(self, user):
        self.user = user
        self.setToolTip(f'{self.user.name} ({self.qtd})' if self.qtd >
                        0 else self.user.name)

    def getBrowser(self):
        return self.browser

    def closeBrowser(self):
        self.browser.stop()
        self.browser.close()

    def doReloadPage(self):
        self.browser.doReload()

    def saveSettings(self):
        self.user.zoomFactor = self.browser.zoomFactor()
        UserDAO.update(self.user)

    def setZoomFactorPage(self, factor=None):
        if factor == None:
            self.browser.setZoomFactor(1.0)
        else:
            self.browser.setZoomFactor(self.browser.zoomFactor()+factor)

    def setThemePage(self, isNight_mode):
        self.browser.whats.setTheme(isNight_mode)

    def setSpellChecker(self, lang):
        profile = self.browser.page().profile()
        profile.setSpellCheckLanguages([lang])

    def closeConversation(self):
        script = """var openConvoClassName = "_3xTHG";
                    var connectingClassName = "_2dfCc";
                    var moreOptionsButtonClassName = "_26lC3";
                    var closeConvoClassName = "_2oldI dJxPU";
 
                    function closeConversation() {
                        var elements = document.getElementsByClassName(openConvoClassName);
                        if (elements.length == 0) {
                            console.debug("Couldn't find an open conversation");
                            return;
                        }
                        console.debug("Conversation open");
                        var moreOptions = document.getElementsByClassName(moreOptionsButtonClassName)[4];
                        moreOptions.click();
                        setTimeout(function() {
                            var buttons = document.getElementsByClassName(closeConvoClassName);
                            if (buttons.length === 6) {
                                moreOptions.click();
                                return;
                            }
                            var index = buttons.length === 9 ? 4 : 2;
                            document.getElementsByClassName(closeConvoClassName)[index].click()
                        }, 1);
                    }
                    closeConversation();
                    """
        self.browser.page().runJavaScript(script)

    ## EVENTS ##

    def selected(self):
        self.isSelected = True
        self.setStyleSheet(self.styleSheet_hover)

    def unselected(self):
        self.isSelected = False
        self.setStyleSheet(self.styleSheet_normal)

    def enterEvent(self, e):
        self.setStyleSheet(self.styleSheet_hover)

    def leaveEvent(self, e):
        if not self.isSelected:
            self.setStyleSheet(self.styleSheet_normal)
