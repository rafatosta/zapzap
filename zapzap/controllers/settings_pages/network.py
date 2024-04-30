from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6 import QtNetwork
from PyQt6.QtCore import QSettings, pyqtSignal
from zapzap.view.network_page import Ui_Network
from gettext import gettext as _
from .tools import updateTextCheckBox
import zapzap


class Network(QWidget, Ui_Network):
    emitUpdateProxyPage = pyqtSignal()

    proxyType = {'NoProxy': (QtNetwork.QNetworkProxy.ProxyType.NoProxy, _("No proxying is used")),
                 'DefaultProxy': (QtNetwork.QNetworkProxy.ProxyType.DefaultProxy, _("Proxy is determined based on the application proxy set using setApplicationProxy()")),
                 'Socks5Proxy': (QtNetwork.QNetworkProxy.ProxyType.Socks5Proxy, _("Socks5 proxying is used")),
                 'HttpProxy': (QtNetwork.QNetworkProxy.ProxyType.HttpProxy, _("HTTP transparent proxying is used")),
                 'HttpCachingProxy': (QtNetwork.QNetworkProxy.ProxyType.HttpCachingProxy, _("Proxying for HTTP requests only")),
                 'FtpCachingProxy': (QtNetwork.QNetworkProxy.ProxyType.FtpCachingProxy, _("Proxying for FTP requests only")),
                 }

    def __init__(self):
        super(Network, self).__init__()
        self.setupUi(self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)

        self.btn_ok.clicked.connect(self.setProxyApp)
        self.btn_restore.clicked.connect(self.restoreProxy)
        self.load()

    def text_changed(self, s):  # s is a str
        self.proxyDescription.setText(self.proxyType[s][1])

    def load(self):
        # Carrega dados do combobox
        self.proxyComboBox.addItems(list(self.proxyType.keys()))
        self.proxyComboBox.currentTextChanged.connect(self.text_changed)

        self.proxyComboBox.setCurrentText(self.settings.value(
            "proxy/proxyType", "NoProxy", str))

        self.proxyDescription.setText(self.proxyType[self.settings.value(
            "proxy/proxyType", "NoProxy", str)][1])

        self.setHostName.setText(self.settings.value(
            "proxy/hostName", "", str))
        self.setPort.setText(self.settings.value(
            "proxy/port", "", str))
        self.setUser.setText(self.settings.value(
            "proxy/user", "", str))
        self.setPassword.setText(self.settings.value(
            "proxy/password", "", str))

        self.proxyCheckBox.setChecked(self.settings.value(
            "proxy/proxyEnable", False, bool))
        self.frameProxy.setEnabled(self.proxyCheckBox.isChecked())

        if self.proxyCheckBox.isChecked():
            self.setProxyApp()

        for children in self.findChildren(QCheckBox):
            children.clicked.connect(self.checkClick)
            updateTextCheckBox(children)

    def checkClick(self):
        children = self.sender()
        childrenName = children.objectName()

        if childrenName == 'proxyCheckBox':
            self.frameProxy.setEnabled(self.proxyCheckBox.isChecked())

        if not self.proxyCheckBox.isChecked():
            self.emitUpdateProxyPage.emit()

        updateTextCheckBox(children)
        self.save()

    def setProxyApp(self):
        self.proxyApp = QtNetwork.QNetworkProxy()
        self.proxyApp.setType(
            self.proxyType[self.proxyComboBox.currentText()][0])

        if self.proxyComboBox.currentText() != 'NoProxy':
            self.proxyApp.setHostName(
                self.setHostName.text()) if self.setHostName.text() != '' else ''
            try:
                self.proxyApp.setPort(
                    int(self.setPort.text())) if self.setPort.text() != '' else ''
            except:
                pass

            self.proxyApp.setUser(
                self.setUser.text()) if self.setUser.text() != '' else ''
            self.proxyApp.setPassword(
                self.setPassword.text()) if self.setPassword.text() != '' else ''

        QtNetwork.QNetworkProxy.setApplicationProxy(self.proxyApp)

        self.save()

        self.emitUpdateProxyPage.emit()

    def restoreProxy(self):
        self.proxyApp = QtNetwork.QNetworkProxy()
        self.proxyApp.setType(
            self.proxyType['NoProxy'][0])
        QtNetwork.QNetworkProxy.setApplicationProxy(self.proxyApp)

        # Limpa as configurações
        self.proxyComboBox.setCurrentText("NoProxy")
        self.proxyDescription.setText(self.proxyType["NoProxy"][1])

        self.setHostName.clear()
        self.setPort.clear()
        self.setUser.clear()
        self.setPassword.clear()

        self.save()

    def save(self):
        self.settings.setValue("proxy/proxyEnable",
                               self.proxyCheckBox.isChecked())
        self.settings.setValue(
            "proxy/proxyType", self.proxyComboBox.currentText())
        self.settings.setValue("proxy/hostName", self.setHostName.text())
        self.settings.setValue("proxy/port", self.setPort.text())
        self.settings.setValue("proxy/user", self.setUser.text())
        self.settings.setValue("proxy/password", self.setPassword.text())
