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
    background-color: #596870;
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
    background-color: #31363b;
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
    color: #F0F2F5;
    background-color: #596870;
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

QMenu::indicator:non-exclusive:unchecked,
QMenu::indicator:non-exclusive:unchecked:selected
{
    border-image: url({path}/checkbox_unchecked_disabled.svg);
}

QMenu::indicator:non-exclusive:checked,
QMenu::indicator:non-exclusive:checked:selected
{
    border-image: url({path}/checkbox_checked.svg);
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
    font-family: Segoe UI
} 
#notify_desktop
{
    color: #eff0f1;
    margin-bottom: 0.09em;
    font: 14pt; 
}
QCheckBox
{
    color: #eff0f1;
    background-color: #202C33;
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
	background-color:  #202C33;
}
QStackedWidget {	
	background-color:  #202C33;
}
/* MENUS */
#menu .QPushButton {	
	background-position: left center;
    background-repeat: no-repeat;
	border: 8px solid  #202C33;
    border-radius: 5px;
	text-align: left;
	padding-left: 44px;
    font: 12pt;
}

#menu .QPushButton:hover {
	background-color: #596870;
    border-color: #596870;
}
#menu .QPushButton:pressed {	
	background-color: #424D53;
    border-color: #424D53;
}

#btn_home{
	background-image: url({path}/home.svg);
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
#btn_donations{
	background-image: url({path}/donations.svg);
}
#btn_about{
	background-image: url({path}/about.svg);
}

#btn_buy_paypal:hover,
#btn_pix:hover{
    color: #A7A8FF;
    text-decoration: underline; 
}

#frameSettings,
#frameAppearance,
#frameTray,
#frameNotifications,
#frameNotificationsPreview,
#frameMenuBar {
    background-color: #202C33;
    border: 2px solid rgba(0, 0, 0,0.1);
    border-radius: 5px;
}

QRadioButton
{
    spacing: 0.23em;
    outline: none;
    color: #eff0f1;
    margin-bottom: 0.09em;
    
}
QRadioButton:disabled
{
    color: #bab9b8;
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

STYLE_SHEET_DARK = f"""
{QWIDGET}
{QMENU_BAR}
{QMENU}
{SettingsMenu}
""".replace("{path}", path)
