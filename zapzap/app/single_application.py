"""Single-instance QApplication implementation."""

import subprocess
import sys

from PyQt6.QtCore import Qt, QTextStream, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import QApplication


class SingleApplication(QApplication):
    RESTART_MESSAGE = "zapzap://restart"

    messageReceived = pyqtSignal(str)

    def __init__(self, appid, *argv):
        super(SingleApplication, self).__init__(*argv)
        self._appid = appid
        self._activationWindow = None
        self._activateOnMessage = False
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self._appid)
        self._isRunning = self._outSocket.waitForConnected()
        self._outStream = None
        self._inSocket = None
        self._inStream = None
        self._server = None
        self.window = None
        self._window_factory = None
        self._interface_restarting = False

        if self._isRunning:
            self._outStream = QTextStream(self._outSocket)
            for message in argv[0]:
                if 'whatsapp' in message or message == self.RESTART_MESSAGE:
                    self.sendMessage(message)
                    break
            sys.exit(0)
        else:
            error = self._outSocket.error()
            if error == QLocalSocket.LocalSocketError.ConnectionRefusedError:
                self.close()
                QLocalServer.removeServer(self._appid)
            self._outSocket = None
            self._server = QLocalServer()
            self._server.listen(self._appid)
            self._server.newConnection.connect(self._onNewConnection)

    def close(self):
        if self._inSocket:
            self._inSocket.disconnectFromServer()
        if self._outSocket:
            self._outSocket.disconnectFromServer()
        if self._server:
            self._server.close()

    def isRunning(self):
        return self._isRunning

    def appid(self):
        return self._appid

    def activationWindow(self):
        return self._activationWindow

    def setActivationWindow(self, activationWindow, activateOnMessage=True):
        self._activationWindow = activationWindow
        self._activateOnMessage = activateOnMessage

    def activateWindow(self):
        if not self._activationWindow:
            return
        self._activationWindow.setWindowState(
            self._activationWindow.windowState() & ~Qt.WindowState.WindowMinimized)
        self._activationWindow.show()
        self._activationWindow.raise_()
        self._activationWindow.activateWindow()

    def sendMessage(self, msg):
        if not self._outStream:
            return False
        self._outStream << msg << '\n'
        self._outStream.flush()
        return self._outSocket.waitForBytesWritten()

    @pyqtSlot()
    def _onNewConnection(self):
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QTextStream(self._inSocket)
        self._inSocket.readyRead.connect(self._onReadyRead)
        if self._activateOnMessage:
            self.activateWindow()

    @pyqtSlot()
    def _onReadyRead(self):
        while True:
            msg = self._inStream.readLine()
            if not msg:
                break
            self.messageReceived.emit(msg)

    def setWindow(self, window):
        self.window = window

    def getWindow(self):
        return self.window

    def startInterface(self, window_factory):
        """Create and register the main interface window."""
        self._window_factory = window_factory
        return self._create_interface_window()

    def restartInterface(self, show=True):
        """Rebuild the MainWindow without restarting the QApplication process.

        This is useful for settings that only need a new MainWindow/browser tree.
        Settings consumed before QApplication/QtWebEngine initialization still need
        a full application restart.
        """
        if not self._window_factory or self._interface_restarting:
            return False

        self._interface_restarting = True
        QTimer.singleShot(0, lambda: self._restart_interface_now(show))
        return True

    def restartApplication(self):
        """Restart the full application process."""
        if self._interface_restarting:
            return False

        self._interface_restarting = True
        QTimer.singleShot(0, self._restart_application_now)
        return True

    def shutdownInterface(self):
        """Release resources owned by the current interface window."""
        if not self.window:
            return

        browser = getattr(self.window, "browser", None)
        if browser:
            browser.shutdown()

    def _restart_application_now(self):
        if self.window and hasattr(self.window, "_save_window_state"):
            self.window._save_window_state()

        self.shutdownInterface()
        self.close()

        restart_args = [arg for arg in sys.argv if arg != self.RESTART_MESSAGE]
        if self._start_detached_process([sys.executable, *restart_args]):
            self.exit(0)
        else:
            self._interface_restarting = False

    def _start_detached_process(self, command):
        try:
            subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError:
            return False

        return True

    def _restart_interface_now(self, show=True):
        old_window = self.window
        was_visible = old_window.isVisible() if old_window else False

        if old_window:
            if hasattr(old_window, "_save_window_state"):
                old_window._save_window_state()
            self.shutdownInterface()
            old_window.hide()
            old_window.deleteLater()

        new_window = self._create_interface_window()
        if show and was_visible:
            new_window.show()

        self._interface_restarting = False

    def _create_interface_window(self):
        window = self._window_factory()
        self.setWindow(window)
        self.setActivationWindow(window)
        window.load_settings()
        from zapzap.features.tray.sys_tray_manager import SysTrayManager
        SysTrayManager.bind_window(window)
        return window
