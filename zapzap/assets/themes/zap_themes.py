from zapzap.assets.themes.style import buildTheme
import zapzap

LIGHT = '#F0F2F5'
DARK = '#202C33'
BLUE = '#34B7F1'


class ZPallete():
    window = ''  # A general background color.
    windowText = ''  # A general foreground color.
    button = ''  # The general button background color.
    buttonText = ''  # A foreground color used with the color.
    buttonHover = ''  # A hover color used with the color.
    highlight = ''  # A color to indicate a selected item or the current item.
    highlightedText = ''  # A text color that contrasts with.
    link = ''  # A text color used for unvisited hyperlinks
    path = '' 

    def __init__(self) -> None:
        pass

    def getPallete(self):
        return {'window': self.window,
                'windowText': self.windowText}


def getThemeLight() -> str:
    p = ZPallete()
    p.window = LIGHT
    p.windowText = DARK

    p.path = zapzap.abs_path + '/assets/themes/light'

    return buildTheme(p)


def getThemeDark() -> str:
    return ''
