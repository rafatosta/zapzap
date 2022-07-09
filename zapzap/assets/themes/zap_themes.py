from zapzap.assets.themes.style import buildTheme
import zapzap

LIGHT = '#F0F2F5'
LIGHT_GRAY = '#BBBCBF'
BLAK_GRAY = '#585A5D'
GRAY = '#bab9b8'
DARK = '#202C33'
BLUE = '#34B7F1'


class ZPallete():
    window = ''  # Uma cor de fundo geral.
    windowText = ''  # Uma cor geral para texto.
    disabled = ''  # Itens desabilitados
    button = ''  # A cor geral de fundo do botão.
    buttonText = ''  # A foreground color used with the color.
    buttonHover = ''  # A hover color used with the color.
    highlight = ''  # Uma cor para indicar um item selecionado ou o item atual.
    # Uma cor de texto que contrasta com o item selecionado.
    highlightedText = ''
    link = ''  # A text color used for unvisited hyperlinks
    path = ''

    def __init__(self) -> None:
        pass

    def getPallete(self):
        return {'window': self.window,
                'windowText': self.windowText,
                'disabled': self.disabled,
                'highlight': self.highlight,
                'highlightedText': self.highlightedText,
                'path': self.path}


def getThemeLight() -> str:
    p = ZPallete()
    p.window = LIGHT
    p.windowText = DARK
    p.disabled = GRAY
    p.highlight = LIGHT_GRAY
    p.highlightedText = DARK
    p.path = zapzap.abs_path + '/assets/themes/light'
    print(p.path)
    return buildTheme(p)


def getThemeDark() -> str:
    p = ZPallete()
    p.window = DARK
    p.windowText = LIGHT
    p.disabled = GRAY
    p.highlight = BLAK_GRAY
    p.highlightedText = LIGHT
    p.path = zapzap.abs_path + '/assets/themes/dark'

    return buildTheme(p)
