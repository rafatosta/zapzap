"""Application bootstrap and lifecycle orchestration."""

import sys

import zapzap
from PyQt6.QtCore import QCoreApplication, QTimer
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap.app.single_application import SingleApplication
from zapzap.app.desktop_application_dbus import DesktopApplicationDBus
from zapzap.app.zapzap_control_dbus import ZapZapControlDBus
from zapzap.app.main_window_controller import MainWindowController
from zapzap.features.browser.shell.browser_controller import (
    load_webview_factory,
)
from zapzap.app.startup_options import apply_startup_options, parse_startup_options
from zapzap.app.unix_signal_bridge import install_unix_signal_bridge
from zapzap.app.window_lifecycle import ClientSideWindowHost
from zapzap.core.diagnostics import crash_handler
from zapzap.assets.icons.tray_icon import TrayIcon
from zapzap.core.environment.proxy_manager import ProxyManager
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.config.settings.system import SystemSettings
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.core.update_checker import UpdateChecker, UpdateState
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.initial_setup.controller import InitialSetupController
from zapzap.features.donation.controller import DonationController
from zapzap.features.dictionaries.system_dictionary_provisioner import (
    SystemDictionaryProvisioner,
)
from zapzap.features.notifications.notification_service import (
    NotificationService,
    is_flatpak,
)
from zapzap.features.reporting.coordinator import ReportingCoordinator
from zapzap.core.reporting.capture import CrashSessionMonitor


def create_main_window(
    webview_factory=None,
    update_state=None,
    update_checker=None,
):
    """Build a fresh MainWindow instance using the current runtime settings."""
    content = MainWindowController(
        webview_factory=webview_factory,
        update_state=update_state,
        update_checker=update_checker,
    )
    window = (
        ClientSideWindowHost(content)
        if AppearanceSettings().csr_enabled
        else content
    )
    if DonationController.should_show():
        DonationController.showMessage(parent=window)
    return window


def main():
    # Desativa todos os prints do código
    # sys.stdout = open(os.devnull, 'w')

    args, _unknown = parse_startup_options()
    apply_startup_options(args)

    # QStandardPaths must know the stable application identity before the
    # managed WebEngine dictionary directory is resolved by SetupManager.
    QCoreApplication.setApplicationName(zapzap.__appname__)
    QCoreApplication.setOrganizationDomain(zapzap.__domain__)

    SetupManager.apply()
    TranslationManager.apply()

    # Qt requires QWebEngineView to be imported (or the corresponding
    # application attribute to be set) before constructing QCoreApplication.
    # Resolve the real factory here; isolated tools inject their QWidget stub.
    webview_factory = load_webview_factory()

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
    unix_signal_bridge = install_unix_signal_bridge(app)
    crash_session_monitor = CrashSessionMonitor(
        logs_provider=lambda: (
            crash_handler.faulthandler_path.read_text(
                encoding="utf-8",
                errors="replace",
            )[-16000:]
            if crash_handler.faulthandler_path.exists()
            else ""
        )
    )
    crash_session_monitor.start()

    SetupManager.apply_qt_scale_factor_rounding_policy()

    # QNetworkProxy is application-wide. Apply the sole global configuration
    # before any controller can construct a functional WebEngine profile.
    ProxyManager.apply()

    def handle_instance_message(result):
        if result == app.RESTART_MESSAGE:
            app.restartApplication()
            return
        # JSON control via QLocalServer (fallback sin D-Bus)
        if result.strip().startswith("{"):
            try:
                import json as _json
                data = _json.loads(result)
                if data.get("action") in ("open_chat", "send", "send_to"):
                    # lazy import para evitar ciclo
                    from zapzap.app.zapzap_control_dbus import ZapZapControlAdaptor
                    # crea adaptor efímero sobre ventana actual para reusar lógica
                    w = app.getWindow()
                    if w is not None:
                        # acceso al page directo
                        try:
                            browser = getattr(w, "browser", None)
                            if browser is None and hasattr(w, "inner_window"):
                                browser = getattr(w.inner_window, "browser", None)
                            webview = browser.current_webview() if browser else None
                            page = webview.page() if webview else None
                        except Exception:
                            page = None
                        act = data.get("action")
                        if act == "open_chat":
                            phone = data.get("phone", "")
                            # usa deeplink
                            from zapzap.features.browser.web.deeplink import build_open_chat_script
                            import urllib.parse
                            # normaliza phone a url
                            digits = "".join(c for c in phone if c.isdigit())
                            if digits.startswith("0") and len(digits)==10:
                                digits="593"+digits[1:]
                            elif len(digits)==9:
                                digits="593"+digits
                            url = f"https://wa.me/{digits}"
                            script = build_open_chat_script(url)
                            if script and page:
                                page.runJavaScript(script)
                                w.show(); w.raise_(); w.activateWindow()
                        elif act == "send":
                            text = data.get("text","")
                            if page and text:
                                import json as _j
                                from zapzap.app.zapzap_control_dbus import SEND_MESSAGE_JS_TEMPLATE
                                js = SEND_MESSAGE_JS_TEMPLATE % _j.dumps(text)
                                page.runJavaScript(js)
                        elif act == "send_to":
                            phone = data.get("phone","")
                            text = data.get("text","")
                            if phone and page:
                                digits = "".join(c for c in phone if c.isdigit())
                                if digits.startswith("0") and len(digits)==10:
                                    digits="593"+digits[1:]
                                elif len(digits)==9:
                                    digits="593"+digits
                                url = f"https://wa.me/{digits}"
                                script = build_open_chat_script(url)
                                if script:
                                    page.runJavaScript(script)
                                    w.show(); w.raise_(); w.activateWindow()
                                    if text:
                                        from PyQt6.QtCore import QTimer as _QTimer
                                        import json as _j2
                                        from zapzap.app.zapzap_control_dbus import SEND_MESSAGE_JS_TEMPLATE as _TPL
                                        js2 = _TPL % _j2.dumps(text)
                                        _QTimer.singleShot(1800, lambda: page.runJavaScript(js2))
                        return
            except Exception:
                pass
        app.getWindow().xdgOpenChat(result)

    # Callback instance
    app.messageReceived.connect(handle_instance_message)

    # Initialize ThemeManager
    ThemeManager.start()

    # The session state survives interface-only restarts, preventing a second
    # request while restoring an already-known update in the rebuilt UI.
    update_state = UpdateState(app)
    update_checker = UpdateChecker(update_state, app)

    # Create main window
    main_window = app.startInterface(
        lambda: create_main_window(
            webview_factory,
            update_state,
            update_checker,
        )
    )

    system_dictionary_provisioner = SystemDictionaryProvisioner(app)
    system_dictionary_provisioner.dictionary_installed.connect(
        lambda _code: app.getWindow().browser.update_spellcheck()
    )
    system_dictionary_provisioner.start()
    desktop_application_dbus = None
    if is_flatpak():
        desktop_application_dbus = DesktopApplicationDBus(app)
        desktop_application_dbus.start()

    # Control D-Bus: siempre activo (AppImage, nativo, Flatpak) para automatización
    zapzap_control_dbus = ZapZapControlDBus(app, app.getWindow)
    zapzap_control_dbus.start()

    # Compatibilidade com comportamento legado de primeiro acesso
    if SettingsManager.get("website/open_page", True):
        QDesktopServices.openUrl(QUrl(zapzap.__website__))
        SettingsManager.set("website/open_page", False)

    should_show_initial_setup = InitialSetupController.should_show()

    if (
        SystemSettings().start_in_background or '--hideStart' in sys.argv
    ) and not should_show_initial_setup:
        main_window.hide()
    else:
        main_window.show()

    if should_show_initial_setup:
        QTimer.singleShot(
            0, lambda: InitialSetupController(app.getWindow()).exec())
    else:
        reporting_coordinator = ReportingCoordinator(app.getWindow())
        app._reporting_coordinator = reporting_coordinator
        QTimer.singleShot(0, reporting_coordinator.show_prepared_crash)

    app.aboutToQuit.connect(NotificationService.shutdown)
    app.aboutToQuit.connect(crash_session_monitor.close)
    app.aboutToQuit.connect(system_dictionary_provisioner.close)
    if desktop_application_dbus is not None:
        app.aboutToQuit.connect(desktop_application_dbus.stop)
    app.aboutToQuit.connect(zapzap_control_dbus.stop)
    app.aboutToQuit.connect(ThemeManager.stop)
    app.aboutToQuit.connect(app.shutdownInterface)
    if unix_signal_bridge is not None:
        app.aboutToQuit.connect(unix_signal_bridge.close)

    exit_code = app.exec()

    # Defensive fallback for abnormal shutdown paths where aboutToQuit may not have run.
    NotificationService.shutdown()
    crash_session_monitor.close()
    ThemeManager.stop()
    app.shutdownInterface()
    if unix_signal_bridge is not None:
        unix_signal_bridge.close()

    return exit_code
