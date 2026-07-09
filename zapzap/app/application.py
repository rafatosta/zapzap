"""Application bootstrap and lifecycle orchestration."""

import sys

import zapzap
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

    # Callback instance
    app.messageReceived.connect(lambda result: main_window.xdgOpenChat(result))

    # Initialize ThemeManager
    ThemeManager.start()

    # Create main window
    mainwindow_inside = MainWindowController()
    csr_enabled = SettingsManager.get("system/csr", False)
    main_window = ClientSideRenderingController(
        mainwindow_inside, enabled=True) if csr_enabled else mainwindow_inside
    app.setWindow(main_window)
    app.setActivationWindow(main_window)
    main_window.load_settings()

    ProxyManager.apply()

    # Compatibilidade com comportamento legado de primeiro acesso
    if SettingsManager.get("website/open_page", True):
        QDesktopServices.openUrl(QUrl(zapzap.__website__))
        SettingsManager.set("website/open_page", False)

    if (
        SettingsManager.get("system/start_background",
                            False) or '--hideStart' in sys.argv
    ):
        main_window.hide()
    else:
        main_window.show()

    app.aboutToQuit.connect(ThemeManager.stop)
    app.aboutToQuit.connect(main_window.browser.shutdown)

    exit_code = app.exec()

    # Defensive fallback for abnormal shutdown paths where aboutToQuit may not have run.
    ThemeManager.stop()
    main_window.browser.shutdown()

    return exit_code
