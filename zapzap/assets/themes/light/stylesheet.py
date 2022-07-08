# Theme Light
from PyQt6.QtCore import QSettings
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
    background-color: rgb(222, 221, 218);
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
    background-color: #FFFFFF;
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
    background-color: rgb(222, 221, 218);
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

QWIDGETS = """
QWidget{
    color: #31363b;
    /*background-color: #F0F2F5; deixa borda nos componentes*/
    selection-background-color: #00A884;
    selection-color: #31363b;
    background-clip: border;
    border-image: none;
    font-family: Segoe UI
}

QStackedWidget {	
	background-color: #F0F2F5;
}
"""

QCHECHBOX = """
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

QRADIONBUTTON = """
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

QSCROLLAREA = """
#system_scrollArea,
#appearance_scrollArea,
#notification_scrollArea,
#donations_scrollArea,
#about_scrollArea {
	background-color: #F0F2F5;
	background: #F0F2F5;
}
QScrollBar:horizontal
    {
        height: 15px;
        margin: 3px 15px 3px 15px;
        border: 1px transparent #2A2929;
        border-radius: 4px;
        background-color: yellow;    /* #2A2929; */
    }

    QScrollBar::handle:horizontal
    {
        background-color: blue;      /* #605F5F; */
        min-width: 5px;
        border-radius: 4px;
    }

    QScrollBar::add-line:horizontal
    {
        margin: 0px 3px 0px 3px;
        border-image: url(:/qss_icons/rc/right_arrow_disabled.png);
        width: 10px;
        height: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:horizontal
    {
        margin: 0px 3px 0px 3px;
        border-image: url(:/qss_icons/rc/left_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on
    {
        border-image: url(:/qss_icons/rc/right_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }


    QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on
    {
        border-image: url(:/qss_icons/rc/left_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
    {
        background: none;
    }


    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
    {
        background: none;
    }

    QScrollBar:vertical
    {
        background-color: #2A2929;
        width: 15px;
        margin: 15px 3px 15px 3px;
        border: 1px transparent #2A2929;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical
    {
        background-color: red;         /* #605F5F; */
        min-height: 5px;
        border-radius: 4px;
    }

    QScrollBar::sub-line:vertical
    {
        margin: 3px 0px 3px 0px;
        border-image: url(:/qss_icons/rc/up_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:vertical
    {
        margin: 3px 0px 3px 0px;
        border-image: url(:/qss_icons/rc/down_arrow_disabled.png);
        height: 10px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on
    {
        border-image: url(:/qss_icons/rc/up_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on
    {
        border-image: url(:/qss_icons/rc/down_arrow.png);
        height: 10px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
    {
        background: none;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
    {
        background: none;
    }
"""

SettingsMenu = """
#leftMenu,
#leftBar_2
{	
	background-color: #F0F2F5;
}
#menu .QPushButton {	
	background-position: left center;
    background-repeat: no-repeat;
	border: 8px solid #F0F2F5;
    border-radius: 5px;
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
    color: #5C5EBD;
    text-decoration: underline; 
}
"""

FrameSetting = """
#frameSettings,
#frameAppearance,
#frameTray,
#frameNotifications,
#frameNotificationsPreview,
#frameMenuBar,
#frame_experiments {
    background-color: #F0F2F5;
    border: 2px solid rgba(0, 0, 0,0.1);
    border-radius: 5px;
}
"""

ZapDecoration = """
#app {	
	background-color: #F0F2F5;
	border: 3px solid #E4E5E5; 
    border-radius: 10px;
}
#headbar{	
	background-color: #F0F2F5;
    border: 3px solid #F0F2F5; 
    border-radius: 10px;
}

#rightButtons .QPushButton {	
	background-position: center;
    background-repeat: no-repeat;
	border: 0px solid #F0F2F5;
}

#leftButtons .QPushButton {	
	background-position: center;
    background-repeat: no-repeat;
	border: 0px solid #F0F2F5;
}


#closeAppBtn,
#closeAppBtn_left{
	background-image: url({path}/btn_close.svg);
}

#closeAppBtn:hover,
#closeAppBtn_left:hover{
	background-image: url({path}/btn_close_hover.svg);
}

#settingsTopBtn,
#settingsTopBtn_left{
	background-image: url({path}/btn_settings.svg);
}
"""


settings = QSettings(zapzap.__appname__, zapzap.__appname__)
if not settings.value("system/zap_decoration", False, bool):
    ZapDecoration = ""

STYLE_SHEET_LIGHT = f"""
{QMENU_BAR}
{QMENU}
{QWIDGETS}
{QCHECHBOX}
{QRADIONBUTTON}
{QSCROLLAREA}
{SettingsMenu}
{FrameSetting}
{ZapDecoration}
""".replace("{path}", path)
