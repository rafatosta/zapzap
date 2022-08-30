from zapzap.theme.style import buildTheme
import zapzap

LIGHT = '#F0F2F5'
LIGHT_GRAY = '#BBBCBF'
BLAK_GRAY = '#585A5D'
GRAY = '#bab9b8'
DARK = '#202C33'
BLUE = '#00A884'
WRITE = '#FFFFFF'


class ZPallete():
    window = ''  # Uma cor de fundo geral.
    windowText = ''  # Uma cor geral para texto.
    disabled = ''  # Itens desabilitados
    highlight = ''  # Uma cor para indicar um item selecionado ou o item atual.
    # Uma cor de texto que contrasta com o item selecionado.
    highlightedText = ''
    link = ''  # A text color used for unvisited hyperlinks
    path = ''
    path_btn_titlebar = ''
    frame_background = ''
    frame_border = ''
    frame_background_popup = ''

    def __init__(self) -> None:
        pass

    def setPath(self, path):
        self.path = zapzap.abs_path + '/assets/icons/app/'+path

    def setPathBtnTitlebar(self, path):
        self.path_btn_titlebar = zapzap.abs_path + \
            '/assets/icons/titlebar_buttons/'+path

    def getPallete(self):
        return {'window': self.window,
                'windowText': self.windowText,
                'disabled': self.disabled,
                'highlight': self.highlight,
                'highlightedText': self.highlightedText,
                'link': self.link,
                'path': self.path,
                'path_btn_titlebar': self.path_btn_titlebar,
                'frame_background': self.frame_background,
                'frame_border': self.frame_border,
                'frame_background_popup': self.frame_background_popup}


def getThemeLight() -> str:
    p = ZPallete()
    p.window = LIGHT
    p.windowText = DARK
    p.disabled = GRAY
    p.highlight = LIGHT_GRAY
    p.highlightedText = DARK
    p.link = BLUE
    p.frame_background = WRITE
    p.frame_border = 'rgba(0, 0, 0, 0.1)'
    p.frame_background_popup = WRITE
    p.setPath('light')
    p.setPathBtnTitlebar('default/light')
    return buildTheme(p)


def getThemeDark() -> str:
    p = ZPallete()
    p.window = DARK
    p.windowText = LIGHT
    p.disabled = BLAK_GRAY
    p.highlight = BLAK_GRAY
    p.highlightedText = LIGHT
    p.link = BLUE
    p.frame_background = 'rgba(0, 0, 0, 0.2)'
    p.frame_border = 'rgba(0, 0, 0, 0.3)'
    p.frame_background_popup = DARK
    p.setPath('dark')
    p.setPathBtnTitlebar('default/dark')

    return buildTheme(p)
