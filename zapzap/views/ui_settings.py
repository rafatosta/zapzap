from gettext import gettext as _
# Form implementation generated from reading ui file './zapzap/ui/ui_settings.ui'
#
# Created by: PyQt6 UI code generator 6.8.1.dev2502011625
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(700, 518)
        Settings.setWindowTitle("")
        Settings.setStyleSheet("")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Settings)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sidebar = QtWidgets.QFrame(parent=Settings)
        self.sidebar.setMinimumSize(QtCore.QSize(300, 0))
        self.sidebar.setMaximumSize(QtCore.QSize(300, 16777215))
        self.sidebar.setStyleSheet("")
        self.sidebar.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.sidebar.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.sidebar.setObjectName("sidebar")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.sidebar)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.menu_layout = QtWidgets.QFrame(parent=self.sidebar)
        self.menu_layout.setStyleSheet("")
        self.menu_layout.setObjectName("menu_layout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.menu_layout)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btn_back = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_back.setObjectName("btn_back")
        self.verticalLayout_2.addWidget(self.btn_back)
        spacerItem = QtWidgets.QSpacerItem(20, 172, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.label_4 = QtWidgets.QLabel(parent=self.menu_layout)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.line_3 = QtWidgets.QFrame(parent=self.menu_layout)
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_2.addWidget(self.line_3)
        self.btn_page_general = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_page_general.setObjectName("btn_page_general")
        self.verticalLayout_2.addWidget(self.btn_page_general)
        self.btn_account = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_account.setCheckable(False)
        self.btn_account.setChecked(False)
        self.btn_account.setObjectName("btn_account")
        self.verticalLayout_2.addWidget(self.btn_account)
        self.label_3 = QtWidgets.QLabel(parent=self.menu_layout)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.line = QtWidgets.QFrame(parent=self.menu_layout)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.btn_page_appearence = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_page_appearence.setObjectName("btn_page_appearence")
        self.verticalLayout_2.addWidget(self.btn_page_appearence)
        self.btn_page_notifications = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_page_notifications.setObjectName("btn_page_notifications")
        self.verticalLayout_2.addWidget(self.btn_page_notifications)
        self.btn_page_performance = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_page_performance.setObjectName("btn_page_performance")
        self.verticalLayout_2.addWidget(self.btn_page_performance)
        self.btn_page_network = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_page_network.setObjectName("btn_page_network")
        self.verticalLayout_2.addWidget(self.btn_page_network)
        self.label = QtWidgets.QLabel(parent=self.menu_layout)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.line_4 = QtWidgets.QFrame(parent=self.menu_layout)
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout_2.addWidget(self.line_4)
        self.btn_page_help = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_page_help.setObjectName("btn_page_help")
        self.verticalLayout_2.addWidget(self.btn_page_help)
        spacerItem1 = QtWidgets.QSpacerItem(20, 171, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.btn_quit = QtWidgets.QPushButton(parent=self.menu_layout)
        self.btn_quit.setObjectName("btn_quit")
        self.verticalLayout_2.addWidget(self.btn_quit)
        self.verticalLayout.addWidget(self.menu_layout)
        self.horizontalLayout.addWidget(self.sidebar)
        self.pages = QtWidgets.QStackedWidget(parent=Settings)
        self.pages.setObjectName("pages")
        self.horizontalLayout.addWidget(self.pages)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        
        self.btn_back.setText(_("Back"))
        self.label_4.setText(_("SETTINGS"))
        self.btn_page_general.setText(_("General"))
        self.btn_account.setText(_("Accounts"))
        self.label_3.setText(_("TOOLS"))
        self.btn_page_appearence.setText(_("Appearance"))
        self.btn_page_notifications.setText(_("Notifications"))
        self.btn_page_performance.setText(_("Performance"))
        self.btn_page_network.setText(_("Network"))
        self.label.setText(_("HELP"))
        self.btn_page_help.setText(_("About"))
        self.btn_quit.setText(_("Quit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Settings = QtWidgets.QWidget()
    ui = Ui_Settings()
    ui.setupUi(Settings)
    Settings.show()
    sys.exit(app.exec())
