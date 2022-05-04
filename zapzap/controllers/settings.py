from PyQt6.QtWidgets import QWidget, QTabBar
from PyQt6 import uic
from PyQt6.QtCore import QSize, Qt
from zapzap.controllers.settings_about import Settings_About
from zapzap.controllers.settings_notify import Settings_Notify
from zapzap.controllers.settings_system import Settings_System
from zapzap.controllers.settings_users import Settings_Users
from zapzap.services.portal_theme import isDarkTheme
import zapzap


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        w = int(self.width()/self.count())
        return QSize(w, size.height())


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(zapzap.abs_path+'/view/settings.ui', self)

        self.parent = parent

        self.tabs.setTabBar(TabBar())
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        #self.tabs.addTab(Settings_Users(), "Users")
        self.tabs.addTab(Settings_System(self), "System")
        self.tabs.addTab(Settings_Notify(), "Notifications")
        self.tabs.addTab(Settings_About(), "About")

        self.closeButton.clicked.connect(parent.onToggled)

        if isDarkTheme(): #dark
            self.frame.setStyleSheet("""QFrame#frame {border: 1px solid rgb(192, 191, 188);border-radius: 10px;background-color: #353535;}""")
        else: #light
            self.frame.setStyleSheet("""QFrame#frame {border: 1px solid rgb(192, 191, 188);border-radius: 10px;background-color: rgb(246, 245, 244);}""")



    def mousePressEvent(self, event):
        pass
