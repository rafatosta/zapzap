# Theme Dark
import zapzap

path = zapzap.abs_path + '/assets/themes/dark'

QMENU_BAR = """
QMenuBar
{
    background-color: #202C33;
    color: #F0F2F5;
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
    background-color: #00A884;
    color: #F0F2F5;
    margin-bottom: -0.09em;
    padding-bottom: 0.09em;
}
"""

QMENU = """
QMenu
{
    color: #F0F2F5;
    margin: 0.09em;
}

QMenu::icon
{
    margin: 0.23em;
}

QMenu::item
{
    /* Add extra padding on the right for the QMenu arrow */
    padding: 0.1em 0.5em 0.1em 0.5em;
    border: 0.09em solid transparent;
    background: transparent;
}

QMenu::item:selected
{
    color: #202C33;
    background-color: #00DCAD;
}

QMenu::item:selected:disabled
{
    background-color: #202C33;
}

QMenu::item:disabled
{
    color: #bab9b8;
}

QMenu::indicator
{
    width: 0.8em;
    height: 0.8em;
    /* To align with QMenu::icon, which has a 0.23em margin. */
    margin-left: 0.3em;
    subcontrol-position: center left;
}

QMenu::indicator:non-exclusive:unchecked
{
    border-image: url({path}/checkbox_unchecked_disabled.svg);
}

QMenu::indicator:non-exclusive:unchecked:selected
{
    border-image: url({path}/checkbox_unchecked_disabled.svg);
}

QMenu::indicator:non-exclusive:checked
{
    border-image: url({path}/checkbox_checked.svg);
}

QMenu::indicator:non-exclusive:checked:selected
{
    border-image: url({path}/checkbox_checked_selected.svg);
}

QMenuBar::item:focus:!disabled
{
}
QMenu::separator
{
    height: 0.03em;
    background-color: #bab9b8;
    padding-left: 0.2em;
    margin-top: 0.2em;
    margin-bottom: 0.2em;
    margin-left: 0.41em;
    margin-right: 0.41em;
}
"""

QWIDGET = """
QWidget{
    color: #eff0f1;
    background-color: #202C33;
    selection-background-color: #00A884;
    selection-color: #eff0f1;
    background-clip: border;
    border-image: none;
}
"""

STYLE_SHEET_DARK = f"""
{QWIDGET}
{QMENU_BAR}
{QMENU}
""".replace("{path}", path)
