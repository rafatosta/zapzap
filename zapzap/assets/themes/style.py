from PyQt6.QtCore import QSettings
import zapzap


def buildTheme(p) -> str:
    QWIDGETS = """
        QWidget{
            color: {windowText};
            /*selection-background-color: #00A884;*/
            selection-color: {windowText};
            background-clip: border;
            border-image: none;
            font-family: Segoe UI
        }

        QStackedWidget {	
            background-color: {window};
        }
    """

    QMENU_BAR = """
    QMenuBar
    {
        background-color: {window};
        color: #31363b;
    }

    QMenuBar::item
    {
        background: transparent;
    }

    QMenuBar::item:selected
    {
        background: transparent;
    }

    QMenuBar::item:disabled
    {
        color: #bab9b8;
    }

    QMenuBar::item:pressed
    {
        background-color: rgb(222, 221, 218);
        color: #31363b;
        margin-bottom: -0.09em;
        padding-bottom: 0.09em;
    }
    """

    STYLE_SHEET = f"""
        {QWIDGETS}
        {QMENU_BAR}
        """

    for chave, valor in p.getPallete().items():
        print(f'{chave} : {valor}')
        STYLE_SHEET = STYLE_SHEET.replace("{"+chave+"}", valor)
    print(STYLE_SHEET)

    return STYLE_SHEET
