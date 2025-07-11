from gettext import gettext as _
# Form implementation generated from reading ui file './zapzap/ui/ui_page_notifications.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_PageNotifications(object):
    def setupUi(self, PageNotifications):
        PageNotifications.setObjectName("PageNotifications")
        PageNotifications.resize(693, 620)
        PageNotifications.setWindowTitle("")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(PageNotifications)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.frame = QtWidgets.QFrame(parent=PageNotifications)
        self.frame.setMinimumSize(QtCore.QSize(550, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.frame)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.notify_groupBox = QtWidgets.QGroupBox(parent=self.frame)
        self.notify_groupBox.setCheckable(True)
        self.notify_groupBox.setObjectName("notify_groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.notify_groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.show_photo = QtWidgets.QCheckBox(parent=self.notify_groupBox)
        self.show_photo.setChecked(True)
        self.show_photo.setObjectName("show_photo")
        self.verticalLayout.addWidget(self.show_photo)
        self.show_name = QtWidgets.QCheckBox(parent=self.notify_groupBox)
        self.show_name.setChecked(True)
        self.show_name.setObjectName("show_name")
        self.verticalLayout.addWidget(self.show_name)
        self.show_msg = QtWidgets.QCheckBox(parent=self.notify_groupBox)
        self.show_msg.setChecked(True)
        self.show_msg.setObjectName("show_msg")
        self.verticalLayout.addWidget(self.show_msg)
        self.verticalLayout_2.addWidget(self.notify_groupBox)
        self.donationMessage = QtWidgets.QCheckBox(parent=self.frame)
        self.donationMessage.setObjectName("donationMessage")
        self.verticalLayout_2.addWidget(self.donationMessage)
        self.horizontalLayout.addWidget(self.frame)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 295, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)

        self.retranslateUi(PageNotifications)
        QtCore.QMetaObject.connectSlotsByName(PageNotifications)

    def retranslateUi(self, PageNotifications):
        
        self.label.setText(_("Notifications"))
        self.notify_groupBox.setTitle(_("Work area notifications"))
        self.show_photo.setText(_("Show the photo of the sender"))
        self.show_name.setText(_("Show the sender\'s name"))
        self.show_msg.setText(_("Show message preview"))
        self.donationMessage.setText(_("Hide donation notification"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PageNotifications = QtWidgets.QWidget()
    ui = Ui_PageNotifications()
    ui.setupUi(PageNotifications)
    PageNotifications.show()
    sys.exit(app.exec())
