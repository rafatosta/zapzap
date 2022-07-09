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

    QCHECHBOX = """
        QCheckBox
        {
            color: {windowText};
            margin-bottom: 0.09em;
            font: 11pt;
        }

        QCheckBox:disabled
        {
            color: {disabled};
        }
        QCheckBox::indicator
        {
            width: 24px;
            height: 24px;
        }
        QCheckBox::indicator:unchecked,
        QCheckBox::indicator:unchecked:focus
        {
            border-image: url({path}/checkbox_unchecked_disabled.svg);
        }
        QCheckBox::indicator:unchecked:hover,
        QCheckBox::indicator:unchecked:pressed
        {
            border: none;
            border-image: url({path}/checkbox_unchecked.svg);
        }

        QCheckBox::indicator:checked
        {
            border-image: url({path}/checkbox_checked.svg);
        }

        QCheckBox::indicator:checked:hover,
        QCheckBox::indicator:checked:focus,
        QCheckBox::indicator:checked:pressed
        {
            border: none;
            border-image: url({path}/checkbox_checked.svg);
        }

        QCheckBox::indicator:indeterminate
        {
            border-image: url({path}/checkbox_indeterminate.svg);
        }

        QCheckBox::indicator:indeterminate:focus,
        QCheckBox::indicator:indeterminate:hover,
        QCheckBox::indicator:indeterminate:pressed
        {
            border-image: url({path}/checkbox_indeterminate.svg);
        }

        QCheckBox::indicator:indeterminate:disabled
        {
            border-image: url({path}/checkbox_indeterminate_disabled.svg);
        }

        QCheckBox::indicator:checked:disabled
        {
            border-image: url({path}/checkbox_checked_disabled.svg);
        }

        QCheckBox::indicator:unchecked:disabled
        {
            border-image: url({path}/checkbox_unchecked_disabled.svg);
        }

    """

    QRADIONBUTTON = """
        QRadioButton
        {
            spacing: 0.23em;
            outline: none;
            color: {windowText};
            margin-bottom: 0.09em;
        }
        QRadioButton:disabled
        {
            color: {disabled};
        }

        QRadioButton::indicator
        {
            width: 150px;
            height: 100px;
        }

        #rb_system::indicator:unchecked,
        #rb_system::indicator:unchecked:focus,
        #rb_system::indicator:unchecked:hover,
        #rb_system::indicator:unchecked:pressed
        {
            border-image: url({path}/theme_system_unchecked.svg);
        }

        #rb_system::indicator:checked,
        #rb_system::indicator:checked:hover,
        #rb_system::indicator:checked:focus,
        #rb_system::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/theme_system_checked.svg);
        }

        #rb_light::indicator:unchecked,
        #rb_light::indicator:unchecked:focus,
        #rb_light::indicator:unchecked:hover,
        #rb_light::indicator:unchecked:pressed
        {
            border-image: url({path}/theme_light_unchecked.svg);
        }

        #rb_light::indicator:checked,
        #rb_light::indicator:checked:hover,
        #rb_light::indicator:checked:focus,
        #rb_light::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/theme_light_checked.svg);
        }

        #rb_dark::indicator:checked,
        #rb_dark::indicator:checked:hover,
        #rb_dark::indicator:checked:focus,
        #rb_dark::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/theme_dark_checked.svg);
        }

        #rb_dark::indicator:unchecked,
        #rb_dark::indicator:unchecked:focus,
        #rb_dark::indicator:unchecked:hover,
        #rb_dark::indicator:unchecked:pressed
        {
            border-image: url({path}/theme_dark_unchecked.svg);
        }

        #rb_tray_default::indicator:unchecked,
        #rb_tray_default::indicator:unchecked:focus,
        #rb_tray_default::indicator:unchecked:hover,
        #rb_tray_default::indicator:unchecked:pressed
        {
            border-image: url({path}/tray_default_unchecked.svg);
        }

        #rb_tray_default::indicator:checked,
        #rb_tray_default::indicator:checked:hover,
        #rb_tray_default::indicator:checked:focus,
        #rb_tray_default::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/tray_default_checked.svg);
        }

        #rb_tray_light::indicator:unchecked,
        #rb_tray_light::indicator:unchecked:focus,
        #rb_tray_light::indicator:unchecked:hover,
        #rb_tray_light::indicator:unchecked:pressed
        {
            border-image: url({path}/tray_light_unchecked.svg);
        }

        #rb_tray_light::indicator:checked,
        #rb_tray_light::indicator:checked:hover,
        #rb_tray_light::indicator:checked:focus,
        #rb_tray_light::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/tray_light_checked.svg);
        }

        #rb_tray_dark::indicator:unchecked,
        #rb_tray_dark::indicator:unchecked:focus,
        #rb_tray_dark::indicator:unchecked:hover,
        #rb_tray_dark::indicator:unchecked:pressed
        {
            border-image: url({path}/tray_dark_unchecked.svg);
        }

        #rb_tray_dark::indicator:checked,
        #rb_tray_dark::indicator:checked:hover,
        #rb_tray_dark::indicator:checked:focus,
        #rb_tray_dark::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/tray_dark_checked.svg);
        }
    """


    STYLE_SHEET = f"""
        {QWIDGETS}
        {QMENU_BAR}
        {QMENU}
        {QCHECHBOX}
        {QRADIONBUTTON}
        """

    for chave, valor in p.getPallete().items():
        #print(f'{chave} : {valor}')
        STYLE_SHEET = STYLE_SHEET.replace("{"+chave+"}", valor)
    # print(STYLE_SHEET)

    return STYLE_SHEET
