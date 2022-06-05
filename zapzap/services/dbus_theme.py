from PyQt6 import QtDBus


def get_system_theme():
    """ Available color schemes:
    - 0: No preference (True)
    - 1: Prefer dark appearance
    - 2: Prefer light appearance (True)
    """
    try:
        name = "org.freedesktop.portal.Desktop"
        path = "/org/freedesktop/portal/desktop"
        interface = "org.freedesktop.portal.Settings"

        smp = QtDBus.QDBusInterface(name, path, interface)
        msg = smp.call('Read', "org.freedesktop.appearance", 'color-scheme')
        color_sheme = msg.arguments()[0]
        print(f'Current color: {color_sheme}')
        return False if (color_sheme == 0) or color_sheme == 2 else True
    except Exception:
        return False
