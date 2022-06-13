# Theme Light
import zapzap

path = zapzap.abs_path + '/assets/themes/light'

QMENU_BAR = """
QMenuBar
{
    background-color: #F0F2F5;
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
    background-color: #bab9b8;
    color: #31363b;
    margin-bottom: -0.09em;
    padding-bottom: 0.09em;
}
"""

QMENU = """
QMenu
{
    color: #31363b;
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
    color: #31363b;
    background-color: #00DCAD;
}

QMenu::item:selected:disabled
{
    background-color: #F0F2F5;
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
    color: #31363b;
    /*background-color: #F0F2F5; deixa borda nos componentes*/
    selection-background-color: #00A884;
    selection-color: #31363b;
    background-clip: border;
    border-image: none;
}
"""

SettingsMenu = """
#leftMenu {	
	background-color: #F0F2F5;
}
/* MENUS */
#menu .QPushButton {	
	background-position: left center;
    background-repeat: no-repeat;
	border: none;
	border-radius: 5px;
	/*border-left: 22px solid transparent;*/
	background-color: transparent;
	text-align: left;
	padding-left: 44px;
}
#menu .QPushButton:hover {
	background-color: rgb(222, 221, 218);
}
#menu .QPushButton:pressed {	
	background-color: rgb(192, 191, 188);
}
/* Back Button */
#btn_back {
	background-position: left center;
    background-repeat: no-repeat;
	border: none;
	text-align: left;
	padding-left: 44px;
	/*color: rgb(113, 126, 149);*/
}
#btn_back:hover {
	
}
#btn_back:pressed {
	
}
"""

STYLE_SHEET_LIGHT = f"""
{QWIDGET}
{QMENU_BAR}
{QMENU}
{SettingsMenu}
""".replace("{path}", path)

