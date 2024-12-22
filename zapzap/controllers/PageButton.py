from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize

from zapzap.models import User
from zapzap.resources.TrayIcon import TrayIcon


class PageButton(QPushButton):

    number_notifications = 0

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
      background-color: rgba(225, 225, 225, 0.3);
      border-radius: 2px;
      height: 30px;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding:2px;
    }
    """

    styleSheet_selected = """
    QPushButton {
      background-color: rgba(225, 225, 225, 0.3);
      border-radius: 2px;
      height: 30px;
      border-left: 3px solid #00BD95;
    }
    QToolTip {
       color: #F0F2F5;
       background-color: #202C33;
       padding:2px;
    }
    """

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)

        self.user = user
        self.page_index = page_index

        self.setup_button()

    def setup_button(self):
        self.setFlat(True)
        self.setMinimumSize(QSize(40, 40))
        self.setMaximumSize(QSize(40, 40))
        self.setStyleSheet(self.styleSheet_normal)
        self.setIcon(TrayIcon.getIcon(
            TrayIcon.Type.Default, self.number_notifications))

    def update_notifications(self, number_notifications):
        self.number_notifications = number_notifications
        
        self.setIcon(TrayIcon.getIcon(
            TrayIcon.Type.Default, self.number_notifications))
        self.setToolTip(f'{self.user.name} ({self.number_notifications})' if self.number_notifications >
                        0 else self.user.name)

    ## EVENTS ##

    def selected(self):
        self.isSelected = True
        self.setStyleSheet(self.styleSheet_selected)

    def unselected(self):
        self.isSelected = False
        self.setStyleSheet(self.styleSheet_normal)

    def enterEvent(self, e):
        if not self.isSelected:
            self.setStyleSheet(self.styleSheet_hover)
        else:
            self.setStyleSheet(self.styleSheet_selected)

    def leaveEvent(self, e):
        if not self.isSelected:
            self.setStyleSheet(self.styleSheet_normal)
        else:
            self.setStyleSheet(self.styleSheet_selected)
