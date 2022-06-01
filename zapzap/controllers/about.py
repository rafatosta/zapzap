from PyQt6.QtCore import QSize
import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class About(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/about.ui')

        self.name.setText(zapzap.__appname__)

        self.version.setText(
            f'Version {zapzap.__version__}')
        self.description_app.setText(zapzap.__comment__)
        self.developer.setText('Author: ' + zapzap.__author__)
        self.license.setText(zapzap.__licence__)

        self.icon.setPixmap(zapzap.tray_path.pixmap(QSize(100, 100)))
