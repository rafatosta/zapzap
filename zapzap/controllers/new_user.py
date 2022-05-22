from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap, QIcon
import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class NewUser(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/new_user.ui')
