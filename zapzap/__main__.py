import zapzap
import sys
import argparse

from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from zapzap.config.SetupManager import SetupManager
from zapzap.controllers.MainWindow import MainWindow
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.TranslationManager import TranslationManager
from zapzap.resources.TrayIcon import TrayIcon

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

    # Create main window
    main_window = MainWindow()
    app.setWindow(main_window)
    app.setActivationWindow(main_window)
    main_window.load_settings()

    ProxyManager.apply()

    # Abre site do ZapZap em primeiro acesso
    if SettingsManager.get("website/open_page", True):
        QDesktopServices.openUrl(QUrl(zapzap.__website__))
        SettingsManager.set("website/open_page", False)

    if SettingsManager.get("system/start_background", False) or '--hideStart' in sys.argv:
        main_window.hide()
    else:
        main_window.show()

    # Start app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
