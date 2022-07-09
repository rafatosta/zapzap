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
        QMenuBar {
            background-color: {window};
            color: {windowText};
        }

        QMenuBar::item {
            background: transparent;
        }

        QMenuBar::item:selected {
            background: transparent;
        }

        QMenuBar::item:disabled {
            color: {disabled};
        }

        QMenuBar::item:pressed  {
            background-color: {highlight};
            color: {highlightedText};
            margin-bottom: -0.09em;
            padding-bottom: 0.09em;
        }
    """

    QMENU = """
        QMenu {
            color: {windowText};
            margin: 0.09em;
            background-color: {window};
        }

        QMenu::icon {
            margin: 0.23em;
        }

        QMenu::item  {
            /* Add extra padding on the right for the QMenu arrow */
            padding: 0.1em 0.5em 0.1em 0.5em;
            border: 0.09em solid transparent;
            background: transparent;
        }

        QMenu::item:selected {
            color: {highlightedText};
            background-color: {highlight};
        }

        QMenu::item:selected:disabled  {
            background-color: {disabled};
        }

        QMenu::item:disabled  {
            color: {disabled};
        }

        QMenu::indicator  {
            width: 0.8em;
            height: 0.8em;
            /* To align with QMenu::icon, which has a 0.23em margin. */
            margin-left: 0.3em;
            subcontrol-position: center left;
        }

        QMenu::indicator:non-exclusive:unchecked,
        QMenu::indicator:non-exclusive:unchecked:selected  {
            border-image: url({path}/checkbox_unchecked_disabled.svg);
        }

        QMenu::indicator:non-exclusive:checked,
        QMenu::indicator:non-exclusive:checked:selected  {
            border-image: url({path}/checkbox_checked.svg);
        }

        QMenuBar::item:focus:!disabled { }

        QMenu::separator {
            height: 0.03em;
            background-color: {disabled};
            padding-left: 0.2em;
            margin-top: 0.2em;
            margin-bottom: 0.2em;
            margin-left: 0.41em;
            margin-right: 0.41em;
        }
    """

    STYLE_SHEET = f"""
        {QWIDGETS}
        {QMENU_BAR}
        {QMENU}
        """

    for chave, valor in p.getPallete().items():
        #print(f'{chave} : {valor}')
        STYLE_SHEET = STYLE_SHEET.replace("{"+chave+"}", valor)
    # print(STYLE_SHEET)

    return STYLE_SHEET
