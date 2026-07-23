from PyQt6.QtCore import QStandardPaths, QFileInfo
from zapzap.core.platform import IS_WINDOWS, IS_MAC
from PyQt6.QtCore import QMetaType
from PyQt6.QtDBus import (
    QDBusArgument,
    QDBusConnection,
    QDBusInterface,
    QDBusMessage,
    QDBusVariant,
)

import os


class AutostartManager:
    CONFIG_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.ConfigLocation) + '/autostart/com.rtosta.zapzap.desktop'
    IS_FLATPAK = QFileInfo(__file__).absolutePath().startswith('/app/')

    @staticmethod
    def create_desktop_file(enable_autostart: bool):
        """Creates or removes the autostart desktop entry."""
        if IS_WINDOWS:
            AutostartManager._handle_windows(enable_autostart)
        elif IS_MAC:
            AutostartManager._handle_macos(enable_autostart)
        elif AutostartManager.IS_FLATPAK:
            AutostartManager._handle_flatpak(enable_autostart)
        else:
            AutostartManager._handle_local(enable_autostart)

    @staticmethod
    def _handle_windows(enable_autostart: bool):
        """Manages autostart settings on Windows via the registry."""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                                0, winreg.KEY_SET_VALUE) as key:
                if enable_autostart:
                    import sys
                    exe = sys.executable
                    winreg.SetValueEx(key, "ZapZap", 0, winreg.REG_SZ,
                                      f'"{exe}" -m zapzap --hideStart')
                else:
                    try:
                        winreg.DeleteValue(key, "ZapZap")
                    except FileNotFoundError:
                        pass
        except Exception as e:
            print(f"Error managing Windows autostart: {e}")

    @staticmethod
    def _handle_macos(enable_autostart: bool):
        """Manages autostart settings on macOS via LaunchAgents."""
        try:
            import os
            plist_dir = os.path.expanduser("~/Library/LaunchAgents")
            plist_path = os.path.join(plist_dir, "com.rtosta.zapzap.plist")

            if enable_autostart:
                import sys
                exe = sys.executable
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rtosta.zapzap</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe}</string>
        <string>-m</string>
        <string>zapzap</string>
        <string>--hideStart</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
                os.makedirs(plist_dir, exist_ok=True)
                with open(plist_path, "w") as f:
                    f.write(plist_content)
            else:
                if os.path.exists(plist_path):
                    os.remove(plist_path)
        except Exception as e:
            print(f"Error managing macOS autostart: {e}")

    @staticmethod
    def _handle_flatpak(enable_autostart: bool) -> bool:
        """Manage Flatpak autostart using the XDG Background portal."""

        bus = QDBusConnection.sessionBus()

        interface = QDBusInterface(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.Background",
            bus,
        )

        if not interface.isValid():
            print(
                "Error managing Flatpak autostart: "
                "org.freedesktop.portal.Background is unavailable"
            )
            return False

        # D-Bus type: as (array of strings)
        commandline = QDBusArgument()
        commandline.beginArray(QMetaType.Type.QString.value)
        commandline.add("zapzap")
        commandline.add("--hideStart")
        commandline.endArray()

        # D-Bus type: a{sv}
        options = QDBusArgument()
        options.beginMap(
            QMetaType.Type.QString.value,
            QMetaType.fromName(b"QDBusVariant").id(),
        )

        values = {
            "reason": "Zapzap autostart",
            "autostart": enable_autostart,
            "background": enable_autostart,
            "commandline": commandline,
        }

        for key, value in values.items():
            options.beginMapEntry()
            options.add(key)
            options.add(QDBusVariant(value))
            options.endMapEntry()

        options.endMap()

        reply = interface.call(
            "RequestBackground",
            "",
            options,
        )

        if reply.type() == QDBusMessage.MessageType.ErrorMessage:
            print(
                "Error managing Flatpak autostart: "
                f"{reply.errorName()}: {reply.errorMessage()}"
            )
            return False

        return True

    @staticmethod
    def _handle_local(enable_autostart: bool):
        """Manages autostart settings for local installations."""
        if enable_autostart:
            AutostartManager._create_local_desktop_entry()
        else:
            AutostartManager._remove_local_desktop_entry()

    @staticmethod
    def _create_local_desktop_entry():
        """Creates a local autostart desktop entry."""
        desktop_entry_content = """[Desktop Entry]
Version=1.0
Name=ZapZap
Comment[pt_BR]=Whatsapp Desktop para Linux
Comment=Whatsapp Desktop for Linux
Exec=zapzap %u --hideStart
Icon=com.rtosta.zapzap
Type=Application
Categories=Chat;Network;InstantMessaging;Qt;
Keywords=Whatsapp;Chat;ZapZap;
StartupWMClass=zapzap
MimeType=x-scheme-handler/whatsapp
Terminal=false
SingleMainWindow=true
X-GNOME-UsesNotifications=true
X-GNOME-SingleWindow=true"""

        try:
            with open(AutostartManager.CONFIG_PATH, 'w') as file:
                file.write(desktop_entry_content)
        except Exception as e:
            print(f"Error creating desktop entry: {e}")

    @staticmethod
    def _remove_local_desktop_entry():
        """Removes the local autostart desktop entry."""
        try:
            if os.path.exists(AutostartManager.CONFIG_PATH):
                os.remove(AutostartManager.CONFIG_PATH)
        except Exception as e:
            print(f"Error removing desktop entry: {e}")
