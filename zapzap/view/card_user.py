from gettext import gettext as _
# Form implementation generated from reading ui file './zapzap/view/card_user.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CardUser(object):
    def setupUi(self, CardUser):
        CardUser.setObjectName("CardUser")
        CardUser.resize(620, 120)
        CardUser.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(CardUser)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(CardUser)
        self.frame.setMinimumSize(QtCore.QSize(620, 0))
        self.frame.setMaximumSize(QtCore.QSize(620, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_3.setContentsMargins(15, 15, 15, 15)
        self.gridLayout_3.setHorizontalSpacing(15)
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.icon = QtWidgets.QLabel(self.frame)
        self.icon.setMinimumSize(QtCore.QSize(64, 64))
        self.icon.setMaximumSize(QtCore.QSize(64, 64))
        self.icon.setText("")
        self.icon.setScaledContents(True)
        self.icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.icon.setObjectName("icon")
        self.gridLayout_3.addWidget(self.icon, 1, 0, 1, 1)
        self.id = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.id.sizePolicy().hasHeightForWidth())
        self.id.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.id.setFont(font)
        self.id.setObjectName("id")
        self.gridLayout_3.addWidget(self.id, 0, 0, 1, 3)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.btnDisable = QtWidgets.QPushButton(self.frame)
        self.btnDisable.setObjectName("btnDisable")
        self.gridLayout.addWidget(self.btnDisable, 0, 0, 1, 1)
        self.btnDelete = QtWidgets.QPushButton(self.frame)
        self.btnDelete.setObjectName("btnDelete")
        self.gridLayout.addWidget(self.btnDelete, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 1, 2, 1, 1)
        self.inputGrid = QtWidgets.QGridLayout()
        self.inputGrid.setVerticalSpacing(10)
        self.inputGrid.setObjectName("inputGrid")
        self.keySequenceEdit = QtWidgets.QKeySequenceEdit(self.frame)
        self.keySequenceEdit.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.keySequenceEdit.sizePolicy().hasHeightForWidth())
        self.keySequenceEdit.setSizePolicy(sizePolicy)
        self.keySequenceEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.keySequenceEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.keySequenceEdit.setObjectName("keySequenceEdit")
        self.inputGrid.addWidget(self.keySequenceEdit, 1, 0, 1, 1)
        self.name = QtWidgets.QLineEdit(self.frame)
        self.name.setMinimumSize(QtCore.QSize(0, 0))
        self.name.setReadOnly(True)
        self.name.setObjectName("name")
        self.inputGrid.addWidget(self.name, 0, 0, 1, 2)
        self.gridLayout_3.addLayout(self.inputGrid, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(CardUser)
        QtCore.QMetaObject.connectSlotsByName(CardUser)

    def retranslateUi(self, CardUser):
        
        CardUser.setWindowTitle(_("Form"))
        self.id.setText(_("#id"))
        self.btnDisable.setText(_("Disable"))
        self.btnDelete.setText(_("Delete"))
        self.keySequenceEdit.setKeySequence(_("Ctrl+1"))
        self.name.setText(_("User 0"))
        self.name.setPlaceholderText(_("Usuário padrão"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CardUser = QtWidgets.QWidget()
    ui = Ui_CardUser()
    ui.setupUi(CardUser)
    CardUser.show()
    sys.exit(app.exec())
