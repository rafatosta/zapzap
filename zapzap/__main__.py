import zapzap
import sys
import argparse

from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from zapzap.services.ThemeManager import ThemeManager
from zapzap.services.SetupManager import SetupManager
from zapzap.controllers.MainWindow import MainWindow
from zapzap.controllers.ClientSideRendering import ClientSideRendering
from zapzap.controllers.OnboardingDialog import OnboardingDialog
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.TranslationManager import TranslationManager
from zapzap.resources.TrayIcon import TrayIcon

from zapzap.debug import crash_handler


def main():
    # Desativa todos os prints do código
    # sys.stdout = open(os.devnull, 'w')

    parser = argparse.ArgumentParser(
        description="Gerenciar configurações do zapzap")
    parser.add_argument("--setSettings", nargs=2, metavar=("chave",
                        "valor"), help="Define uma configuração específica")
    parser.add_argument("--wayland", action="store_true",
                        help="Força o uso do Wayland (QT_QPA_PLATFORM=wayland)")
    args, unknown = parser.parse_known_args()

    if args.setSettings:
        chave, valor = args.setSettings
        try:
            print(f"Configurando {chave} para {valor}")
            SettingsManager.set(chave, valor)
        except ValueError:
            print(f"Erro: O valor '{valor}' não é um número inteiro válido.")

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
    mainwindow_inside = MainWindow()
    csr_enabled = SettingsManager.get("system/client_side_rendering", False)
    main_window = ClientSideRendering(mainwindow_inside, enabled=True) if csr_enabled else mainwindow_inside
    app.setWindow(main_window)
    app.setActivationWindow(main_window)
    main_window.load_settings()

    ProxyManager.apply()

    show_onboarding = OnboardingDialog.should_show()

    # Se houver onboarding, abrimos a janela para o fluxo ficar visualmente integrado
    if show_onboarding:
        main_window.show()
        OnboardingDialog.run(main_window)

    # Compatibilidade com comportamento legado de primeiro acesso
    if SettingsManager.get("website/open_page", True):
        QDesktopServices.openUrl(QUrl(zapzap.__website__))
        SettingsManager.set("website/open_page", False)

    if not show_onboarding and (
        SettingsManager.get("system/start_background", False) or '--hideStart' in sys.argv
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


if __name__ == "__main__":
    sys.exit(main())