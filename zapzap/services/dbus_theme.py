from PyQt6 import QtDBus


def getSystemTheme():
    """ Available color schemes:
    - 0: No preference (True)
    - 1: Prefer dark appearance (False)
    - 2: Prefer light appearance (True)
    """
    try:
        name = "org.freedesktop.portal.Desktop"
        path = "/org/freedesktop/portal/desktop"
        interface = "org.freedesktop.portal.Settings"

        smp = QtDBus.QDBusInterface(name, path, interface)
        msg = smp.call('Read', "org.freedesktop.appearance", 'color-scheme')
        color_sheme = msg.arguments()[0]
        return 'light' if (color_sheme == 0) or color_sheme == 2 else 'dark'
    except Exception:
        return 'light'
