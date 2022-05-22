import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class Users(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/users.ui')