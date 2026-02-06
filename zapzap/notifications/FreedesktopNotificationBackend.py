from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage
from PyQt6.QtWidgets import QApplication


class FreedesktopNotificationBackend:
    def __init__(self):
        self.interface = QDBusInterface(
            "org.freedesktop.Notifications",
            "/org/freedesktop/Notifications",
            "org.freedesktop.Notifications",
            QDBusConnection.sessionBus()
        )

    def notify(self, page, notification, title: str, message: str):
        try:
            reply = self.interface.call(
                "Notify",
                "ZapZap",
                0,
                "",            # icon (pode evoluir)
                title,
                message,
                ["default"],   # ação padrão
                {
                    "category": "im.received",
                    "desktop-entry": "com.rtosta.zapzap"
                },
                3000
            )

            if reply.type() == QDBusMessage.MessageType.ErrorMessage:
                raise RuntimeError(reply.errorMessage())

            # Confirma para o WebEngine
            notification.show()

            # Clique → foco da janela
            def on_click():
                main_window = QApplication.instance().getWindow()
                if not main_window:
                    return

                main_window.show()
                main_window.raise_()
                main_window.activateWindow()

                main_window.browser.switch_to_page(
                    page,
                    main_window.browser.page_buttons[page.page_index]
                )

                notification.click()

            try:
                notification.clicked.connect(on_click)
            except Exception as e:
                print('Exception (notification.clicked):', e)

        except Exception as e:
            print('Exception (FreedesktopNotificationBackend):', e)
