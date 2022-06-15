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
QCheckBox
{
    color: #31363b;
    margin-bottom: 0.09em;
    font: 11pt; 
}
QCheckBox:disabled
{
    color: #bab9b8;
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

SettingsMenu = """
#leftMenu,
#leftBar_2
{	
	background-color: #F0F2F5;
}
QStackedWidget {	
	background-color: #F0F2F5;
}
/* MENUS */
#menu .QPushButton {	
	background-position: left center;
    background-repeat: no-repeat;
	border: none;
	border: 8px solid #F0F2F5;
    border-radius: 5px;
	background-color: transparent;
	text-align: left;
	padding-left: 44px;
    font: 12pt; 
}

#menu .QPushButton:hover {
	background-color: rgb(222, 221, 218);
    border-color: rgb(222, 221, 218);
}
#menu .QPushButton:pressed {	
	background-color: rgb(192, 191, 188);
    border-color: rgb(192, 191, 188);
}
/* Back Button */
#btn_back {
	background-position: left center;
    background-repeat: no-repeat;
	border: none;
	text-align: left;
	padding-left: 40px;
    font: 10pt; 
    background-image: url({path}/previous.svg);
}
#btn_back:hover {
	color: #00A884;
}

#btn_home{
	background-image: url({path}/appearance.svg);
}
#btn_system{
	background-image: url({path}/system.svg);
}
#btn_appearance{
	background-image: url({path}/appearance.svg);
}
#btn_notifications{
	background-image: url({path}/notifications.svg);
}
#btn_about{
	background-image: url({path}/about.svg);
}

#frameSettings,
#frameAppearance,
#frameTray,
#frameNotifications,
#frameNotificationsPreview,
#frameMenuBar {
    background-color: rgb(255, 255, 255);
    border: 2px solid rgba(0, 0, 0,0.1);
    border-radius: 5px;
}

QRadioButton
{
    spacing: 0.23em;
    outline: none;
    color: #31363b;
    margin-bottom: 0.09em;
    
}
QRadioButton:disabled
{
    color: #bab9b8;
}

QRadioButton::indicator
{
    width: 70px;
    height: 70px;
}
QRadioButton::indicator:unchecked,
QRadioButton::indicator:unchecked:focus
{
    border-image: url({path}/image_teste.svg);
}
QRadioButton::indicator:unchecked:hover,
QRadioButton::indicator:unchecked:pressed
{
    border: none;
    outline: none;
    border-image: url(zapzap/assets/stylesheets/light/radio_unchecked.svg);
}
QRadioButton::indicator:checked
{
    border: none;
    outline: none;
    border-image: url(zapzap/assets/stylesheets/light/radio_checked.svg);
}

QRadioButton::indicator:checked:hover,
QRadioButton::indicator:checked:focus,
QRadioButton::indicator:checked:pressed
{
    border: none;
    outline: none;
    border-image: url(zapzap/assets/stylesheets/light/radio_checked.svg);
}

QRadioButton::indicator:checked:disabled
{
    outline: none;
    border-image: url(zapzap/assets/stylesheets/light/radio_checked_disabled.svg);
}

QRadioButton::indicator:unchecked:disabled
{
    border-image: url(zapzap/assets/stylesheets/light/radio_unchecked_disabled.svg);
}
"""

STYLE_SHEET_LIGHT = f"""
{QWIDGET}
{QMENU_BAR}
{QMENU}
{SettingsMenu}
""".replace("{path}", path)
