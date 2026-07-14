"""Application bootstrap and lifecycle orchestration."""

import sys

import zapzap
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap.app.single_application import SingleApplication
from zapzap.app.startup_options import apply_startup_options, parse_startup_options
from zapzap.ui.main_window.client_side_rendering_controller import ClientSideRenderingController
from zapzap.ui.main_window.main_window_controller import MainWindowController
from zapzap.core.diagnostics import crash_handler
from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.environment.proxy_manager import ProxyManager
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.initial_setup.controller import InitialSetupController


def create_main_window():
    """Build a fresh MainWindow instance using the current runtime settings."""
    mainwindow_inside = MainWindowController()
    csr_enabled = SettingsManager.get("system/csr", False)
    return ClientSideRenderingController(
        mainwindow_inside, enabled=True) if csr_enabled else mainwindow_inside


def main():
    # Desativa todos os prints do código
    # sys.stdout = open(os.devnull, 'w')

    args, _unknown = parse_startup_options()
    apply_startup_options(args)

    SetupManager.apply()
    TranslationManager.apply()

    # Instala o handler de crash
    crash_handler.install()

    # Define application attributes
    app = SingleApplication(
        zapzap.__appid__, sys.argv + SetupManager.get_argv())
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)
    app.setWindowIcon(TrayIcon.getIcon())

    SetupManager.apply_qt_scale_factor_rounding_policy()

    def handle_instance_message(result):
        if result == app.RESTART_MESSAGE:
            app.restartApplication()
            return

        app.getWindow().xdgOpenChat(result)

    # Callback instance
    app.messageReceived.connect(handle_instance_message)

    # Initialize ThemeManager
    ThemeManager.start()

    # Create main window
    main_window = app.startInterface(create_main_window)

    ProxyManager.apply()

    # Compatibilidade com comportamento legado de primeiro acesso
    if SettingsManager.get("website/open_page", True):
        QDesktopServices.openUrl(QUrl(zapzap.__website__))
        SettingsManager.set("website/open_page", False)

    should_show_initial_setup = InitialSetupController.should_show()

    if (
        SettingsManager.get("system/start_background",
                            False) or '--hideStart' in sys.argv
    ) and not should_show_initial_setup:
        main_window.hide()
    else:
        main_window.show()

    if should_show_initial_setup:
        QTimer.singleShot(
            0, lambda: InitialSetupController(app.getWindow()).exec())

    app.aboutToQuit.connect(ThemeManager.stop)
    app.aboutToQuit.connect(app.shutdownInterface)

    exit_code = app.exec()

    # Defensive fallback for abnormal shutdown paths where aboutToQuit may not have run.
    ThemeManager.stop()
    app.shutdownInterface()

    return exit_code
